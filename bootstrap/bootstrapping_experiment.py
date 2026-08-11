import logging

import pandas as pd
import numpy as np

from bootstrap.models import (    
    BootstrapStatsBinary, 
    BootstrapStatsCategorical, 
    BootstrapStatsContinuous, 
    StatsType,
)

from representativity.smd import SMDCalculator

logger = logging.getLogger(__name__)

class BootstrapExperiment:

    def __init__(
        self,
        data: tuple[pd.DataFrame, pd.DataFrame],
        num_columns: list[str],
        cat_conditions: dict[str, list[str]],
        spc_columns: list[str],
        random_state: int = 42
    ) -> None:
        
        self._df_control, self._df_treatment = data
        self._num_columns = num_columns
        self._cat_conditions = cat_conditions
        self._spc_columns = spc_columns
        self._all_columns = num_columns + list(cat_conditions.keys()) + spc_columns
        self._random_state = random_state

    # Automatization

        self.bootstrap_c, self.bootstrap_t = self._generate_samples()
        self.stats_c = self._calculate_stats(self.bootstrap_c)
        self.stats_t = self._calculate_stats(self.bootstrap_t)
        self.smd = self._calculate_smd()


    #------------------------Private methods-----------------------------------

    def _generate_samples(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        bootstrap_c = self._df_control[self._all_columns].sample(
            n = len(self._df_control),
            replace = True,
            random_state = self._random_state,
        )
        bootstrap_t = self._df_treatment[self._all_columns].sample(
                 n = len(self._df_treatment),
            replace = True,
            random_state = self._random_state,
        )
        return bootstrap_c, bootstrap_t


    # se usa para iterar por grupo, es decir que al invocar
    # debo implementarlo dos veces: uno para que haga cálculos sobre 
    # el grupo control y otro sobre el grupo tratamiento

    def _calculate_stats(
            self,
            bootstrap_samples: pd.DataFrame
    ) -> dict[str, StatsType]:
        """
        Calcula estadísticas resumen para cada columna según su tipo:
        - NUM_COLUMNS -> continua:  media + std + var (BootstrapStatsContinuous)
        - CAT_CONDITIONS -> proporciones por categoría, calculadas sobre la serie completa, no sobre un subcnjunto ya filtrado (BootstrapStatsCategorical)
        - SPC_COLUMNS -> proporción 0-1 de varables bool(BootstrapStatsBinary)
        """

        stats: dict[str, StatsType] = {}
        
        for col in self._num_columns:
            serie = bootstrap_samples[col].dropna()
            stats[col] = self._stats_for_continuous(serie, int(serie.count()))

        for col, allowed_categories in self._cat_conditions.items():
            serie = bootstrap_samples[col].dropna()
            stats[col]= self._stats_for_categorical(serie, allowed_categories)
   
        for col in self._spc_columns:
            serie = bootstrap_samples[col].dropna()
            stats[col] = self._stats_for_binary(serie, int(serie.count()))

        return stats

    # ----------------------------- Private helper methods -----------------------------


    @staticmethod
    def _stats_for_continuous(serie: pd.Series, n:int) -> BootstrapStatsContinuous:
        """ 
        Calcula estadísticas para variables numéricas continuas.
        """
        return BootstrapStatsContinuous(
            mean=float(serie.mean()),
            std = float(serie.std(ddof=1)),
            var=float(serie.var(ddof=1)),
            n=n,
        )
    
    @staticmethod
    def _stats_for_categorical(
        serie:pd.Series, allowed_categories: list[str]
    ) -> BootstrapStatsCategorical:
        """
        Calcula la proporción de cada categoría permitida sobre la serie
        COMPLETA — no sobre un subconjunto ya filtrado a esas categorías.
 
        Si allowed_categories no cubre toda la serie (ej. una condición
        aislada como 'Soy jefa(e)' en vez del listado completo de
        parentescos), el resto se agrupa en "otros" para satisfacer el
        validador proportions.sum() == 1.0 de BootstrapStatsCategorical.
        """
        n = int(serie.count())

        proportions = {
            str(cat): float((serie == cat).sum() / n) for cat in allowed_categories
        }
        if sum(proportions.values()) == 0:
            logger.warning(
                f"Ninguna observación pertenece a las categorías"
                f"{allowed_categories}; revisar si están definidas correctamente."
            )
        
        # Calcular proporciones normalizadas (suman 1)
        residual = 1.0 - sum(proportions.values())
        if residual > 1e-9:
            proportions["otros"] = residual

        return BootstrapStatsCategorical(
            n = n,
            proportions=proportions,
        )

    @staticmethod
    def _stats_for_binary(serie: pd.Series, n: int) -> BootstrapStatsBinary:
        """
        Calculates statistics for Boolean variables (SPC_COLUMNS).
    
        var and std are calculated as p*(1-p) / sqrt(p*(1-p)) — NOT with
        serie.var(ddof=1) — because validate_bernoulli_variance requires
        exact consistency with the theoretical formula (rtol=1e-5), and the
        sample variance with ddof=1 does not satisfy this condition unless n is very large.
        """

        p = float(serie.mean())
        var = p * (1 - p)
        std = float(np.sqrt(var))
        return BootstrapStatsBinary(
            mean=p,
            std=std,
            var=var,
            n=n,
        )

 
    def _calculate_smd(self) -> pd.DataFrame:
        """
        Calcula el balance (SMD) entre grupo control y tratamiento,
        usando self.stats_c / self.stats_t — que ya están calculados sobre
        las muestras BOOTSTRAP (self.bootstrap_c / self.bootstrap_t), no
        sobre self._df_control / self._df_treatment directamente.
 
        Esto no es una elección de diseño: SMDCalculator opera sobre
        objetos BootstrapStats*, no sobre DataFrames, así que stats_c/
        stats_t es la única fuente posible.
        """
        results = []
 
        for col in self._num_columns:
            smd = SMDCalculator.smd_continuous(self.stats_c[col], self.stats_t[col])
            results.append(self._smd_row(col, "continua", smd))
 
        for col in self._spc_columns:
            smd = SMDCalculator.smd_binary(self.stats_c[col], self.stats_t[col])
            results.append(self._smd_row(col, "binaria", smd))
 
        for col in self._cat_conditions:
            smd = SMDCalculator.smd_categorical(
                self.stats_c[col], self.stats_t[col], resumen="max"
            )
            results.append(
                self._smd_row(col, "categórica (max |SMD| entre dummies)", smd)
            )
 
        return (
            pd.DataFrame(results)
            .sort_values("abs_SMD", ascending=False, na_position="last")
            .reset_index(drop=True)
        )
 