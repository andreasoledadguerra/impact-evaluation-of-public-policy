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

# ---------------------------------------------------- Sampling ------------------------------------------------

def simple_random_sample(df: pd.DataFrame, n:int, random_state=42) -> pd.DataFrame:
        return df.sample(n=n,random_state=random_state)


def generate_samples_first(df_control:pd.DataFrame, df_treatment: pd.DataFrame, random_state=42)-> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Extract a simple random sample (SRS) from each group prior to bootstrapping.
    """
    srs_c= simple_random_sample(df_control, SAMPLE_SIZE, random_state)
    srs_t = simple_random_sample(df_treatment,SAMPLE_SIZE, random_state)
    return srs_c, srs_t  
    
# Recibe los dataframes de generate_sample_first y hace cálculos estadísticos sobre ciertas variables(columnas)
def compute_sample_statistics_first(data: tuple[pd.DataFrame, pd.DataFrame]) -> tuple[pd.DataFrame,pd.DataFrame]:
    df_control, df_treatment = data #desempaquetado para poder aplicar los métodos
    stats_c = SampleAnalysis(df_control)
    stats_t = SampleAnalysis(df_treatment)

    return stats_c, stats_t

