
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

from typing import Literal
from bootstrap.models import (
    BootstrapStatsContinuous,
    BootstrapStatsBinary,
    BootstrapStatsCategorical
)

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
                f"resumen debe ser 'max', 'mean' o 'detail', recibido: {resumen!r}"
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