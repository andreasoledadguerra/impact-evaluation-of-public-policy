import pandas as pd
import numpy as np

from src.preprocessing import ProcessedDataframe



# Initialize processed dataframe

processed_df = ProcessedDataframe()

# ------------------------------------ Filtro inicial de candidatos por grupo ----------------------------
def randomization(df: pd.DataFrame) -> pd.DataFrame:

# Se agrupa en 'Tratamiento' si se cumple 'solicitud_adjudicada', y 'control', en caso contrario
    df['grupo'] = np.where(df['state'] == 'solicitud_adjudicada','Tratamiento', 'Control')

    # Guardar extracción de datos en "Control" o "Tratamiento"
    grupo_control = (df['grupo']) == 'Control' # es una serie que devuelve booleanos
    grupo_tratamiento = (df['grupo']) == 'Tratamiento' # idem

    # A cada grupo le damos estructura de dataframe nuevo
    df_control = df[grupo_control]
    df_treatment = df[grupo_tratamiento]

    return df_control, df_treatment

#------------------------------------- Muestreo ------------------------------------
 # Crear una función para calcular muestra
def simple_random_sample(df: pd.DataFrame, n:int, seed=42 ):
     df = df.sample(n=n,random_state=seed)
     return df 

#Método para extraer muestra antes del bootstrapping
def generate_samples_first(df_control:pd.DataFrame, df_treatment: pd.DataFrame)-> tuple[pd.DataFrame, pd.DataFrame]:
    srs_c= simple_random_sample(df_control, SAMPLE_SIZE)
    srs_t = simple_random_sample(df_treatment,SAMPLE_SIZE)
    return srs_c, srs_t  #----> dos muestras en forma de df
    


