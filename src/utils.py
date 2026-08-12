import pandas as pd


# Helper function to calculate mean and standard deviation for a given column
def _calculate_media_std(df: pd.DataFrame, column:str, decimals:int = 1) -> tuple:
    """Calculates the mean and standard deviation of a column. Built-in function."""
    media = round(float(df[column].mean(skipna=True)), decimals)
    std = round(float(df[column].std(skipna=True)), decimals)
    return media, std

# Function to calculate mean and standard deviation for a given column
#def calculate_mean_std(df: pd.DataFrame, column: str, decimals: int = 1):
#    
#    return (
#        f'The mean of {column} is {float(round(df[column].mean(skipna=True), decimals))} ',
#        f'The standard deviation of {column} is {float(round(df[column].std(skipna=True), decimals))}'
#    )
#
#
## Implement a function to calculate the proportion under a condition
#def calculate_conditional_proportion(df: pd.DataFrame, column: str, condition: str, decimals: int = 1) -> tuple[float, float]:
#    """Proporción de filas donde column == condition."""
#    proportion = (df[column] == condition).mean(skipna=True)
#    print(f"The proportion of {condition} in {column} is {round(proportion, decimals)}")
#    return round(float(proportion), decimals)


def calculate_media_std_list(df: pd.DataFrame, lista: list, decimals: int = 1) -> pd.DataFrame:
    """
    Calculate the mean and standard deviation for a list of columns.
    Returns a DataFrame with one row and columns named mean_X and dev_X.
    """
    resultados = {}
    for columna in lista:
        media, std = _calculate_media_std(df, columna)
        resultados[f'media_{columna}'] = media
        resultados[f'desv_{columna}'] = std
    return pd.DataFrame([resultados]) # pandas necesita lista de diccionarios


def calculate_media_condition(df: pd.DataFrame, dict_condiciones: dict, decimals: int = 1) -> pd.DataFrame:
    """
    Calculates the proportion of each categorical value defined in dict_conditions.
    Returns a DataFrame with one row and columns named mean_{col}_{condition}.
    """
    resultado = {}
    for columna, lista_condiciones in dict_condiciones.items():
        for condicion in lista_condiciones:
            proporcion = (df[columna] == condicion).mean(skipna=True)
            resultado[f'media_{columna}_{condicion}'] = round(proporcion, decimals)
    return pd.DataFrame([resultado])