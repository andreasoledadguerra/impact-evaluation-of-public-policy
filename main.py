
import pandas as pd
import numpy as np
from src.randomization import randomization, simple_random_sample
from bootstrap.bootstrapping import get_sample_bootstrap, calculate_mean_bootstrap
from src.sampleanalysis import SampleAnalysis  
from src.utils import Stats
from src.preprocessing import ProcessedDataframe
from bootstrap.models import BoostrapStats
from bootstrap.experiment import BootstrapExperiment


sample_analysis = SampleAnalysis()

SAMPLE_SIZE = 1000

# Generar muestras aleatorias del grupo control y tratamiento 
def generate_samples(df_control:pd.DataFrame, df_treatment: pd.DataFrame)-> tuple[pd.DataFrame, pd.DataFrame]:
    srs_c= simple_random_sample(df_control, SAMPLE_SIZE)
    srs_t = simple_random_sample(df_treatment,SAMPLE_SIZE)
    return srs_c, srs_t  #----> dos muestras en forma de df


#recibe los dataframes de generate_sample
# y hace cálculos estadísticos sobre ciertas variables(columnas)
def compute_sample_statistics(data: tuple[pd.DataFrame, pd.DataFrame]) -> tuple[pd.DataFrame,pd.DataFrame]:
    df_control, df_treatment = data #desempaquetado para poder aplicar los métodos
    stats_c = SampleAnalysis(df_control)
    stats_t = SampleAnalysis(df_treatment)

    return stats_c, stats_t

# -------------------------------- BOOTSTRAPPING ('ingreso_anual_hogar', etc)-----------------------------------------

COLUMNS = ['ingreso_anual_hogar']

#experiment 












# Calcular la media poblacional del ingreso anual del hogar del dataset original
processed_df = ProcessedDataframe()
mean_population_iah = processed_df[COLUMN].mean()

# ---- Coeficiente de representatividad de la muestra de cada grupo sobre la variable "iah" -----
# --------- "representativeness coefficient" -------
# Recibe el output de mean_sample_bootstrap()
# Se necesitan: 
# - las medias de la columna de cada grupo
# - las varianzas de la columna de cada grupo
# - utilizar la Diferencia Estandarizada (Standardized Mean Difference — SMD)

#Interpretación:

# - |SMD| < 0.10 → excelente representatividad
# - |SMD| < 0.25 → aceptable
# - |SMD| ≥ 0.25 → desequilibrio problemático (Cohen, 1988; Austin, 2009)


def calculate_rep_coef(processed_df: pd.DataFrame, sample: tuple[pd.DataFrame, pd.DataFrame], COLUMN: str):
    sample_c, sample_t = sample
    mean_population_iah = processed_df[COLUMN].mean()
    rep_coef_mean = 










median_sample_c = sample_c[COLUMN].median()
median_sample_t = sample_t[COLUMN].median()