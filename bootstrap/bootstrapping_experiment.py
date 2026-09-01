import logging

import pandas as pd
import numpy as np


from bootstrap.column_registry import ColumnRegistry
from bootstrap.models import (    
    BootstrapStatsBinary, 
    BootstrapStatsCategorical, 
    BootstrapStatsContinuous, 
    StatsType,
)

from representativity.smd import SMDCalculator

logger = logging.getLogger(__name__)


class BootstrapResults:

    def __init__(self) -> None:
        self._data: dict[str, dict[str, list[StatsType]]] = {
            "control": {},
            "treatment": {},
        }

    #  
    def __add(self, group:str, column: str, stats: StatsType) -> None:
        if column not in self._data[group]:
            self._data[group][column] = []
        self._data[group][column].append(stats)

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
        self._registry = ColumnRegistry(num_columns, cat_conditions, spc_columns)
        self._random_state = random_state

    # Automatization

        self.bootstrap_c, self.bootstrap_t = self._generate_samples()
        self.stats_c = self._calculate_stats(self.bootstrap_c)
        self.stats_t = self._calculate_stats(self.bootstrap_t)
        self.smd_summary = self._calculate_smd()


    #----------------------------------Private methods-----------------------------------

    def _generate_samples(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        columns = self._registry.columns
        bootstrap_c = self._df_control[columns].sample(
            n = len(self._df_control),
            replace = True,
            random_state = self._random_state,
        )
        bootstrap_t = self._df_treatment[columns].sample(
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
          Calculates summary statistics for each column based on its type:
            - NUM_COLUMNS -> continuous:  mean + std + var (BootstrapStatsContinuous)
            - CAT_CONDITIONS -> proportions by category, calculated over the entire data set, not over a pre-filtered subset (BootstrapStatsCategorical)
            - SPC_COLUMNS -> 0-1 proportion of Boolean variables (BootstrapStatsBinary)
        """

        stats: dict[str, StatsType] = {}
        
        for col in self._registry.continuous_columns:
            serie = bootstrap_samples[col].dropna()
            stats[col] = self._stats_for_continuous(serie, int(serie.count()))

        for col in self._registry.categorical_columns:
            serie = bootstrap_samples[col].dropna()
            allowed_categories = self._registry.allowed_categories(col)
            stats[col]= self._stats_for_categorical(serie, allowed_categories)
   
        for col in self._registry.binary_columns:
            serie = bootstrap_samples[col].dropna()
            stats[col] = self._stats_for_binary(serie, int(serie.count()))

        return stats

    # ----------------------------- Private helper methods -----------------------------


    @staticmethod
    def _stats_for_continuous(serie: pd.Series, n:int) -> BootstrapStatsContinuous:
        """ 
        Calculates statistics for continuous numeric variables.
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
        Calculate the proportion of each allowed category relative to the
        ENTIRE data set—not relative to a subset that has already been filtered to those categories.
        """
        n = int(serie.count())

        proportions = {
            str(cat): float((serie == cat).mean()) for cat in allowed_categories
        }

        if sum(proportions.values()) == 0:
            logger.warning(
                f"Ninguna observación pertenece a las categorías"
                f"{allowed_categories}; revisar si están definidas correctamente."
            )
        
        # Calculate normalized ratios (that sum to 1)
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
        Calculate the (SMD) balance between the control and treatment groups,
        using self.stats_c / self.stats_t.
        """
        results = []
 
        for col in self._registry.continuous_columns:
            smd = SMDCalculator.smd_continuous(self.stats_c[col], self.stats_t[col])
            results.append(self._smd_row(col, "continua", smd))
 
        for col in self._registry.binary_columns:
            smd = SMDCalculator.smd_binary(self.stats_c[col], self.stats_t[col])
            results.append(self._smd_row(col, "binaria", smd))
 
        for col in self._registry.categorical_columns:
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


    @staticmethod
    def _smd_row(variable: str, tipo: str, smd: float) -> dict:
        """
        Generate a row in the SMD summary with balance interpretation
        """
        is_valid = smd is not None and not np.isnan(smd)
        abs_smd = abs(smd) if is_valid else np.nan
 
        if not is_valid:
            balance = "N/A"
        elif abs_smd < 0.10:
            balance = "excelente"
        elif abs_smd < 0.25:
            balance = "aceptable"
        else:
            balance = "desequilibrado"
 
        return {
            "variable": variable,
            "tipo": tipo,
            "SMD": round(smd, 4) if is_valid else np.nan,
            "abs_SMD": round(abs_smd, 4) if is_valid else np.nan,
            "balance": balance,
        }
 