import pandas as pd


class Stats:

    def __init__(self, df:pd.DataFrame, column: str):

        self.df = df
        self.column = column
        self.decimals = decimals
        self.condition = condition
    
    def calculate_mean_std(df: pd.DataFrame, column: str, decimals: int = 1):
        return (
            f'The mean of {column} is {float(round(df[column].mean(skipna=True), decimals))} ',
            f'The standard deviation of {column} is {float(round(df[column].std(skipna=True), decimals))}'
        )
    

    # Implement a function to calculate the proportion under a condition
    def calculate_conditional_proportion(df: pd.DataFrame, column: str, condition: str):
        proportion = (df[column] == condition).mean(skipna=True)
        print(f"The proportion of {condition} in {column} is {round(proportion, 1)}")
        return round(float(proportion), 1)
    
    # Creamos nueva función que calcula media y desviación estándar

    #def calcular_media_std_1(df: pd.DataFrame, columna:str):
     #   media = round(df[columna].mean(skipna=True),1)
     #   std = round(df[columna].std(skipna=True),1)
     #   return media, std

    # Creamos una función que utiliza el cálculo anterior, y transformaciones a dataframe
    def calcular_media_std_lista(df: pd.DataFrame, lista: list):
        resultados = {}
        for columna in lista:
            media, std = calcular_media_std_1(df, columna)
            resultados[f'media_{columna}'] = media
            resultados[f'desv_{columna}'] = std
        return pd.DataFrame([resultados]) # pandas necesita lista de diccionarios