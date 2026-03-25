
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
    def smd_continuous(x1, x2):
        """Cohen's d con SD pooled for continuous variables. 
        ("ingreso_anual_hogar", "personas_por_ambiente")"""
        n1, n2 = len(x1), len(x2)
        m1, m2 = np.mean(x1), np.mean(x2)
        s1, s2 = np.std(x1, ddof=1), np.std(x2, ddof=1)
        sd_pooled = np.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))
        return (m1 - m2) / sd_pooled if sd_pooled > 0 else np.nan

    @staticmethod
    def smd_binary(x1, x2):
        """Cohen (1988) for bool variables.
        (escenario_vulnerabilidad_social, paredes_ext_revocadas )"""
        p1, p2 = np.mean(x1), np.mean(x2)
        sd_pooled = np.sqrt((p1 * (1 - p1) + p2 * (1 - p2)) / 2)
        return (p1 - p2) / sd_pooled if sd_pooled > 0 else np.nan


    #conurbano_interior , sexo_dni

    def smd_categorical(x1, x2, resumen="max"):
        """
        Calcula SMD para variable categórica nominal via dummies (k-1).

        Parameters
        ----------
        x1, x2   : Series de cada grupo
        resumen   : "max"    → retorna el máximo |SMD| (recomendado para balance tables)
                    "mean"   → retorna el promedio de |SMD|
                    "detail" → retorna el dict completo {categoria: SMD}
        """
        # Categorías ordenadas (determinístico) → se omite la última como referencia
        categories = sorted(pd.concat([x1, x2]).astype(str).unique())

        smds = {}
        for cat in categories[:-1]:
            d1 = (x1.astype(str) == cat).astype(float)
            d2 = (x2.astype(str) == cat).astype(float)
            smds[cat] = smd_binary(d1, d2)

        # Filtrar NaN antes de resumir
        valores = [v for v in smds.values() if not np.isnan(v)]

        if resumen == "max":
            return max(valores, key=abs) if valores else np.nan
        elif resumen == "mean":
            return np.mean(np.abs(valores)) if valores else np.nan
        elif resumen == "detail":
            return smds
    

    