
# SMD = (Media grupo experimental – Media grupo control) / Desviación estándar

# Este cálculo se hace después de hacer bootstrapping por grupo

# Necesitamos :
#  - la media del grupo experimental y la media del grupo control sobre la misma variable , 
#  es decir que el cálculo itere sobre las columnas.
# - Desviación estandar

# El cálculo del SMD dependerá del tipo de variable

# ̣---------------------------------------------------------------------------------------------------------------------


import numpy as np
import pandas as pd

from typing import Literal, TYPE_CHECKING
from bootstrap.models import (
    BootstrapStatsContinuous,
    BootstrapStatsBinary,
    BootstrapStatsCategorical,
    StatsType,
)

if TYPE_CHECKING:
    from bootstrap.column_registry import ColumnRegistry


class SMDCalculator:
    
    @staticmethod
    def smd_continuous(
        s1:BootstrapStatsContinuous,
        s2:BootstrapStatsContinuous
    ) -> float:
        """
        Cohen's d con SD pooled for continuous variables. 
        ("ingreso_anual_hogar", "personas_por_ambiente")
        """
        mean_diff = s1.mean - s2.mean
        sd_pooled = np.sqrt((s1.var + s2.var) / 2)
        return float(mean_diff) / sd_pooled if sd_pooled > 0 else np.nan

    @staticmethod
    def smd_binary(s1: BootstrapStatsBinary,
                   s2: BootstrapStatsBinary,
    ) -> float:
        """
        Cohen (1988) for Boolean variables.
        (social_vulnerability_scenario, exterior_walls_plastered)

        Reuse s1.var / s2.var instead of recalculating p*(1-p): it has already been
        validated in the model that var == mean*(1-mean).
        """
        mean_diff = s1.mean - s2.mean
        sd_pooled = np.sqrt((s1.var + s2.var) / 2)
        return float(mean_diff) / sd_pooled if sd_pooled > 0 else np.nan


    #conurbano_interior , sexo_dni
    @staticmethod
    def smd_categorical(
        s1: BootstrapStatsCategorical,
        s2: BootstrapStatsCategorical, 
        resumen: Literal["max", "mean", "detail"] = "max",
    ) -> float | dict[str, float]:
        """
        Calculates SMD for a nominal categorical variable using dummies (k-1).

        Parameters
        ----------
        summary   : “max”    -> returns the maximum |SMD| (recommended for balance tables)
                    “mean”   -> returns the mean of |SMD|
                    “detail” -> returns the complete dictionary {category: SMD}
        """

        # Categorías ordenadas (determinístico) → se omite la última como referencia
        categories = sorted(set(s1.proportions) | set(s2.proportions))

        smds : dict[str, float] = {}
        for cat in categories[:-1]:
            p1 = s1.proportions.get(cat, 0.0)
            p2 = s2.proportions.get(cat, 0.0)
            sd_pooled = np.sqrt((p1 * (1 - p1) + p2 * (1 - p2)) / 2)
            smds[cat] = float((p1 - p2) / sd_pooled) if sd_pooled > 0 else np.nan


        # Filtrar NaN antes de resumir
        valores = [v for v in smds.values() if not np.isnan(v)]

        if resumen == "max":
            return max(valores, key=abs) if valores else np.nan
        elif resumen == "mean":
            return float(np.mean(np.abs(valores))) if valores else np.nan
        elif resumen == "detail":
            return smds
        else:
            raise ValueError(
                f"Summary must be 'max', 'mean' o 'detail', received: {resumen!r}"
            )

    @staticmethod
    def smd_row(column: str, variable_type: str, smd: float) -> dict:
        """
        An SMD summary row with balance interpretation, according to the standard convention (Austin, 2009): 
        |SMD| < 0-10 excellent, < 0.25 acceptable, otherwise unbalanced.
        """
        is_valid = smd is not None and not np.isnan(smd)
        abs_smd = abs(smd) if is_valid else np.nan

        if not is_valid:
            balance = "N/A"
        elif abs_smd < 0.10:
            balance = "Excellent"
        elif abs_smd < 0.25:
            balance = "Acceptable"
        else:
            balance = "Unbalanced"

        return {
            "column": column,
            "variable_type": variable_type,
            "SMD": float(smd) if is_valid else np.nan,
            "abs_SMD": float(abs_smd) if is_valid else np.nan,
            "balance": balance,
        }
    
    @classmethod
    def replica_smd(
        cls,
        stats_c: dict[str, StatsType],
        stats_t: dict[str, StatsType],
        registry: "ColumnRegistry",
    ) -> pd.DataFrame:
        """
        SMD for a bootstrap replica, one per column for accumulate a list and summarize them.
        """
        rows = []

        for col in registry.continuous_columns:
            smd = cls.smd_continuous(stats_c[col], stats_t[col])
            rows.append(cls.smd_row(col, "continuous", smd))

        for col in registry.binary_columns:
            smd = cls.smd_binary(stats_c[col], stats_t[col])
            rows.append(cls.smd_row(col, "binary", smd))

        for col in registry.categorical_columns:
            smd = cls.smd_categorical(stats_c[col], stats_t[col], resumen="max")
            rows.append(cls.smd_row(col, "categorical(max |SMD| between dummies)", smd))

        return pd.DataFrame(rows)

    @staticmethod
    def summarize_bootstrap_replicas(
        replicas: list[pd.DataFrame], ci: float = 0.95
    ) -> pd.DataFrame:
        """
        Summarizes the SMD results from multiple bootstrap replicas, calculating the mean and confidence intervals.
        """
        all_replicas = pd.concat(replicas, ignore_index=True)
        alpha = (1 - ci) / 2
        lower_q, upper_q = alpha, 1 - alpha

        rows = []
        for col_name, group in all_replicas.groupby("column"):
            values = group["SMD"].dropna()
            variable_type = group["variable_type"].iloc[0]

            if values.empty:
                rows.append({
                    "column": col_name,
                    "variable_type": variable_type,
                    "mean_SMD": np.nan,
                    "median_SMD": np.nan,
                    f"ci_lower_{int(ci*100)}": np.nan,
                    f"ci_upper_{int(ci*100)}": np.nan,
                    "std_SMD": np.nan,
                    "n_replicas": 0,
                    "balance": "N/A",
                })

                continue

            mean_smd = float(values.mean())
            abs_mean_smd = abs(mean_smd)
            balance = (
                "Excellent" if abs_mean_smd < 0.10 else
                "Acceptable" if abs_mean_smd < 0.25 else
                "Unbalanced"
            )


            rows.append({
                "column": col_name, 
                "variable_type": variable_type,
                "mean_SMD": mean_smd,
                "median_SMD": float(values.median()),
                f"ci_lower_{int(ci*100)}": float(values.quantile(lower_q)),
                f"ci_upper_{int(ci*100)}": float(values.quantile(upper_q)),
                "std_SMD": float(values.std()),
                "n_replicas": len(values),
                "balance": balance,
            })

        return (
            pd.DataFrame(rows)
            .sort_values("mean_SMD", key=lambda s: s.abs(), ascending=False, na_position="last")
            .reset_index(drop=True)
        )

        
def calculate_rep_coef_smd(
    processed_df: pd.DataFrame,
    sample: tuple[pd.DataFrame, pd.DataFrame],
    column: str,
) -> dict:
    """
    Calculates the representativeness coefficient for each group (control and
    treatment) relative to the original population, for a given column.

    Uses the Standardized Mean Difference (SMD) between the sample mean of each
    group and the population mean, weighted by the population standard deviation.


    Interpretation (Cohen, 1988; Austin, 2009):
        |SMD| < 0.10  -> excellent representativeness
        |SMD| < 0.25  -> acceptable
        |SMD| >= 0.25 -> problematic imbalance

    Args:
        processed_df: DataFrame containing the entire population (post-preprocessing).
        sample: tuple (df_control, df_treatment) containing the extracted samples.
        column: name of the column to evaluate (e.g., “annual_household_income”).

    Returns:
        dict containing population means/standard deviations and the SMD for each group.
    """

    sample_c, sample_t = sample
 
    mean_population = processed_df[column].mean()
    std_population = processed_df[column].std()
 
    mean_c = sample_c[column].mean()
    mean_t = sample_t[column].mean()
 
    # SMD = (media_muestra - media_poblacion) / std_poblacion
    smd_c = (mean_c - mean_population) / std_population
    smd_t = (mean_t - mean_population) / std_population
 
    return {
        "column": column,
        "mean_population": mean_population,
        "std_population": std_population,
        "smd_control": smd_c,
        "smd_treatment": smd_t,
    }