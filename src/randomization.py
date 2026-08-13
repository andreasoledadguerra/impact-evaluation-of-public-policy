import pandas as pd
import numpy as np

from constants import SAMPLE_SIZE
from src.sampleanalysis import SampleAnalysis


# ------------------------------------ Initial filtering of candidates by group ----------------------------
def randomization(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    It is grouped under “Processing” if ‘request_approved’ is true, and under “Control” otherwise
    """
    df['grupo'] = np.where(df['state'] == 'solicitud_adjudicada','Tratamiento', 'Control')

    grupo_control = (df['grupo']) == 'Control' # es una serie que devuelve booleanos
    grupo_tratamiento = (df['grupo']) == 'Tratamiento' # idem

    df_control = df[grupo_control]
    df_treatment = df[grupo_tratamiento]

    return df_control, df_treatment

# ------------------------------------------- Sampling ------------------------------------....

def simple_random_sample(df: pd.DataFrame, n:int, seed=42) -> pd.DataFrame:
        return df.sample(n=n,random_state=seed)

     
#Método para extraer muestra antes del bootstrapping
def generate_samples_first(df_control:pd.DataFrame, df_treatment: pd.DataFrame)-> tuple[pd.DataFrame, pd.DataFrame]:
    srs_c= simple_random_sample(df_control, SAMPLE_SIZE)
    srs_t = simple_random_sample(df_treatment,SAMPLE_SIZE)
    return srs_c, srs_t  #----> dos muestras en forma de df
    
# Recibe los dataframes de generate_sample_first y hace cálculos estadísticos sobre ciertas variables(columnas)
def compute_sample_statistics_first(data: tuple[pd.DataFrame, pd.DataFrame]) -> tuple[pd.DataFrame,pd.DataFrame]:
    df_control, df_treatment = data #desempaquetado para poder aplicar los métodos
    stats_c = SampleAnalysis(df_control)
    stats_t = SampleAnalysis(df_treatment)

    return stats_c, stats_t

