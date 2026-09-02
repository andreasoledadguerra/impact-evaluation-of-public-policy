import logging
from typing import Any

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

    #  helper method to add stats for a specific group and column
    def __add(self, group:str, column: str, stats: StatsType) -> None:
        if column not in self._data[group]:
            self._data[group][column] = []
        self._data[group][column].append(stats)

    # method to extract the bootstrapping distribution according to its field
    def get_distribution(
            self,
            group: str,
            column: str,
            field: str,
            category: str | None = None,
    ) -> np.array:
        if group not in self._data:
            raise ValueError(f"Group '{group}' not found.")
        if column not in self._data[group]:
            raise KeyError(f"Column '{column}' not found in group '{group}'.")

        replicas = self._data[group][column]

        if not replicas:
            return np.array([])

        if category is not None:
            values = [
                getattr(r, "proportions" , {}).get(category, np.nan) for r in replicas

                ]
        else:
            values = [getattr(r, field, np.nan) for r in replicas]

        return np.array(values, dtype=float)

    # Method to calculate percentiles and confidence intervales for a given field and column
    def summarize(self, ci: float = 0.95) -> dict[str, pd.DataFrame]:
        alpha = 1 - ci/ 2
        percentiles = [100 * alpha, 50.0, 100 * (1 - alpha)]

        summary: dict[str, list[dict[str, Any]]] = {"control": [], "treatment": []}

        for group in ("control", "treatment"):
            for col, replicas in self._data[group].items():
                if not replicas:
                    continue

                first = replicas[0]

                # ------- Continuous and Binary Variables -------
                if isinstance(first, (BootstrapStatsContinuous, BootstrapStatsBinary)):
                    for field in ("mean", "std", "var"):
                       dist =self.get_distribution(group, col, field)
                       if len(dist) == 0 or np.all(np.isnan(dist)):
                            continue
                       q_low, q_med, q_high = np.nanpercentile(dist, percentiles)
                       summary[group].append({
                           "column": col,
                           "variable_type": first._class__.__name__,
                           "statistic": field,
                           "mean_bootstrap": float(np.nanmean(dist)),
                           "median_bootstrap": float(q_med),
                           f"ci_lower_{int(ci*100)}": float(q_low),
                           f"ci_upper_{int(ci*100)}": float(q_high),
                           "std_bootstrap": float(np.nanstd(dist, ddof=1)),
                           "n_replicas": len(dist),                        
                        })

                # ------- Categorical Variables -------
                elif isinstance(first, BootstrapStatsCategorical):
                    all_cats = set()
                    for r in replicas:
                        all_cats.update(getattr(r, "proportions", {}).keys())

                    for cat in sorted(all_cats):
                        dist = self.get_distribution(group, col, "proportions", category=cat)
                        if len(dist) == 0:
                            continue
                        q_low, q_med, q_high = np.nanpercentile(dist, percentiles)
                        summary[group].append({
                            "column": col,
                            "variable_type": "BootstrapStatsCategorical",
                            "statistic": f"proportion_{cat}",
                            "mean_bootstrap": float(np.nanmean(dist)),
                            "median_bootstrap": float(q_med),
                            f"ci_lower_{int(ci*100)}": float(q_low),
                            f"ci_upper_{int(ci*100)}": float(q_high),
                            "std_bootstrap": float(np.nanstd(dist, ddof=1)),
                            "n_replicas": len(dist),
                        })
        return{
            "control": pd.DataFrame(summary["control"]),
            "treatment": pd.DataFrame(summary["treatment"]),
        }
    
class BootstrapExperiment:

    def __init__(
        self,
        data: tuple[pd.DataFrame, pd.DataFrame],
        num_columns: list[str],
        cat_conditions: dict[str, list[str]],
        spc_columns: list[str],
        n_bootstrap: int = 10000, # 1000
        random_state: int | np.random.Generator | None = 42
    ) -> None:
        
        self._df_control, self._df_treatment = data
        self._registry = ColumnRegistry(num_columns, cat_conditions, spc_columns)
        self._random_state = random_state
        self._n_bootstrap = n_bootstrap
        self._rng = np.random.default_rng(random_state)

    # Automatization

        #self.bootstrap_c, self.bootstrap_t = self._generate_samples()
        #self.stats_c = self._calculate_stats(self.bootstrap_c)
        #self.stats_t = self._calculate_stats(self.bootstrap_t)
        #self.smd_summary = self._calculate_smd()

        if self._n_bootstrap < 1000:
            logger.warning(
                f"Bootstrapping with {self._n_bootstrap} replicas. "
                f"Consider increasing to 10000 or more for more stable estimates."
            )

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
 