import pandas as pd

from dateutil.relativedelta import relativedelta


class ProcessedDataframe():

    def __init__(self, df: pd.DataFrame ) -> None:
        self.df = df

    # ---------------------------------------- pre-procesamiento ------------------------------
    @staticmethod
    def concatenate_df() -> pd.DataFrame: 
        
        # Descargamos el dataframe con información de los municipios, los inscriptos al programa y los formularios completos por dichos inscriptos
        df_1 = pd.read_excel("ficha_inscriptos.xlsx")
        df_2 = pd.read_excel("formularios_curso.xlsx")

        # Concatenamos dataframes por columna
        df = pd.concat([df_1, df_2], axis=1)

        return df



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

    