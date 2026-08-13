import pandas as pd

from dateutil.relativedelta import relativedelta


class ProcessedDataframe():

    def __init__(self, df: pd.DataFrame ) -> None:
        self.df = df

    # ---------------------------------------- pre-processing ------------------------------
    @staticmethod
    def concatenate_df() -> pd.DataFrame: 

        df_1 = pd.read_excel("ficha_inscriptos.xlsx")
        df_2 = pd.read_excel("formularios_curso.xlsx")

        # Concatenating dataframes by column
        df = pd.concat([df_1, df_2], axis=1)

        return df


    # ------------------------------------------------- Initial filtering of candidates by group ----------------------------
    @staticmethod
    def filter_df(df: pd.DataFrame) -> pd.DataFrame:  

        # We filter only those registered for Stage 1
        df = df[df['etapa_inscripcion'] == 1 ]

        filtro = (df['state'] == 'solicitud_adjudicada') | \
                 (df['state'] == 'solicitud_elegible_rechazadas_por_excedente')

        df = df[filtro].copy()
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

    