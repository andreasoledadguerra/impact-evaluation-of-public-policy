
import pandas as pd
import numpy as np
from src.randomization import randomization, simple_random_sample
from src.bootstrapping import get_sample_bootstrap, calculate_mean_bootstrap
from src.sampleanalysis import SampleAnalysis  
from src.utils import Stats
from src.preprocessing import ProcessedDataframe


sample_analysis = SampleAnalysis()

SAMPLE_SIZE = 1000
COLUMN = ['ingreso_anual_hogar']

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

#
## Usando las condiciones default de la clase
#analysis.sample_media_condition()
#
## Sobreescribiendo para un análisis puntual
#analysis.sample_media_condition(conditions={'sexo_dni': ['F']})
#

# --------------- CONCATENAR RESULTADOS DE AMBOS GRUPOS ---------------------------------

#def concatenate_df(data:tuple[pd.DataFrame, pd.DataFrame]) -> pd.DataFrame:
#    df_control, df_treatment = data
#    df_groups = pd.concat([df_control, df_treatment], axis=1).reset_index(drop=True)
#
#    return df_groups

# -------------------------------- BOOTSTRAPPING 'ingreso_anual_hogar' -----------------------------------------

def generate_sample_bootstrap(data: tuple[pd.DataFrame, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    df_control, df_treatment = data
    bootstrap_c = get_sample_bootstrap(df_control, COLUMN)
    bootstrap_t = get_sample_bootstrap(df_treatment, COLUMN)

    return bootstrap_c, bootstrap_t

def mean_sample_bootstrap(data: tuple[pd.DataFrame, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    df_control, df_treatment = data
    bootstrap_mean_c = calculate_mean_bootstrap(df_control)
    bootstrap_mean_t = calculate_mean_bootstrap(df_treatment)

    return bootstrap_mean_c, bootstrap_mean_t

#Calcular la media poblacional del ingreso anual del hogar del dataset original
processed_df = ProcessedDataframe()
mean_population_iah = processed_df['ingreso_anual_hogar'].mean()

