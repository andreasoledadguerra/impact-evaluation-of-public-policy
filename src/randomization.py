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
    df_tratamiento = df[grupo_tratamiento]

    return df_control, df_tratamiento


#------------------------------------- Muestreo ------------------------------------
# Crear una función para calcular muestra
def simple_random_sample(df: pd.DataFrame, n:int, seed=42 ):
    df = df.sample(n=n,random_state=seed)
    return df 



