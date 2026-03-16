import pandas as pd
import numpy as np


 # Función para obtener una muestra bootstrap
def get_sample_bootstrap(df_sample: pd.DataFrame, column_df_sample: str, random_state: int = 42) -> np.ndarray:
    np.random.seed(random_state)
    return np.random.choice(df_sample[column_df_sample], size=len(df_sample), replace=True)