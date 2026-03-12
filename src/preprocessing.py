import pandas as pd
import numpy as np

from dateutil.relativedelta import relativedelta

class ProcessedDataframe():

    def __init__(self, df):
        self.df = df

    # ---------------------------------------- pre-procesamiento ------------------------------
    def concatenate_df(df_1:pd.DataFrame, df_2: pd.DataFrame, df_3: pd.DataFrame) -> pd.DataFrame: 
        # Descargamos el dataframe con información de los municipios, los inscriptos al programa y los formularios completos por dichos inscriptos
        df_1= pd.read_excel("base_municipios.xlsx")
        df_2 = pd.read_excel("ficha_inscriptos.xlsx")
        df_3= pd.read_excel("formularios_curso.xlsx")

        # Concatenamos dataframes por columna
        df = pd.concat([df_1, df_2, df_3], axis=1)

        return df

    # --------------------------------------- Filtración ------------------------------------------
    #def drop_columns(df:pd.DataFrame) -> pd.DataFrame:
    #    df = df.drop(columns=['codigo_municipio', 'codigo_region', 'nombre_region', 'codigo_area','nombre_area', 'seccion_electoral',
    #            'superficie(km2)', 'intendente', 'partido_politico_actual', 
    #        'poblacion_censo_2010', 'poblacion_censo_2022'
    #        ])
    #
    #    df = df.drop(['municipio'], axis=1, inplace=True)
    #    return df


    def filter_df(df: pd.DataFrame) -> pd.DataFrame:   

        # Filtramos solo los inscriptos en etapa 1
        df = df[df['etapa_inscripcion'] == 1 ]

        #Filtramos solo los inscriptos en estado solicitud_adjudicada ó solicitud_elegible_rechazadas_por_excedente 
        df[df['state'] == 'solicitud_adjudicada']
        df[df['state'] =='solicitud_elegible_rechazadas_por_excedente']

        # Asignamos variable al filtro de los inscriptos en estado solicitud_adjudicada ó solicitud_elegible_rechazadas_por_excedente
        filtro = (df['state'] == 'solicitud_adjudicada') | \
                 (df['state'] == 'solicitud_elegible_rechazadas_por_excedente')

        # Creamos el nuevo dataframe aplicando el filtro
        df = df[filtro]
        return df

    ## --------------------------- Cálculo de atributo faltante (edad) -----------------------------
    def calculate_age(df: pd.DataFrame) -> pd.DataFrame:
        # Como los valores de cada columna son de distinto tipo de dato, transformamos 'fecha_de_nacimiento' y 'fecha de_carga'
        df.loc['fecha_de_nacimiento'] = pd.to_datetime(
            df['fecha_de_nacimiento'],
            errors='coerce'
        )

        df.loc['fecha_carga'] = pd.to_datetime(
            df['fecha_carga'],
            errors='coerce'
        )

        #TODO:ver función lambda
        # Calcular edad aplicando relativedelta fila a fila
        df['edad'] = df.apply(
            lambda row: relativedelta(row['fecha_carga'], row['fecha_de_nacimiento']).years 
                        if pd.notnull(row['fecha_de_nacimiento']) else pd.NA,
            axis=1
        )
        return df
    # --------------------------......... Cálculo directo de media -----------------------------------------
    def calculate_mean(df: pd.DataFrame) -> pd.DataFrame:
        df['escenario_vulnerabilidad_social'] = float(round(df['escenario_vulnerabilidad_social'].mean(skipna=True), 1))
        df['paredes_ext_revocadas'] = round(df['paredes_ext_revocadas'].mean(skipna=True), 1)
        return df
    