
# SMD = (Media grupo experimental – Media grupo control) / Desviación estándar

# Este cálculo se hace después de hacer bootstrapping por grupo

# Necesitamos :
#  - la media del grupo experimental y la media del grupo control sobre la misma variable , 
#  es decir que el cálculo itere sobre las columnas.
# - Desviación estandar

# El cálculo del SMD dependerá del tipo de variable

import numpy as np
import pandas as pd

def smd_continuous(x1, x2):
    """Cohen's d con SD pooled for continuous variables. 
    ("ingreso_anual_hogar", "personas_por_ambiente")"""
    n1, n2 = len(x1), len(x2)
    m1, m2 = np.mean(x1), np.mean(x2)
    s1, s2 = np.std(x1, ddof=1), np.std(x2, ddof=1)
    sd_pooled = np.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))
    return (m1 - m2) / sd_pooled if sd_pooled > 0 else np.nan
