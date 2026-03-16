
import pandas as pd
import numpy as np
from src.randomization import randomization, simple_random_sample
from src.sampleanalysis import SampleAnalysis  
from src.utils import Stats

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

#
## Usando las condiciones default de la clase
#analysis.sample_media_condition()
#
## Sobreescribiendo para un análisis puntual
#analysis.sample_media_condition(conditions={'sexo_dni': ['F']})
#

# --------------- CONCATENAR RESULTADOS DE AMBOS GRUPOS ---------------------------------

# Crear un dataframe resumen del grupo control
df_media_condición_control = calcular_media_condicion(df_control_clean, dict_condiciones)
df_media_std_control = calcular_media_std_lista(df_control_clean, lista_c)
df_mean_control = pd.concat([fila_vuln_c, fila_per_c], axis= 1)

