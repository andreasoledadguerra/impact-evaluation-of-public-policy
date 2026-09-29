import pandas as pd

from dateutil.relativedelta import relativedelta
from config import MUNICIPIOS_PATH, INSCRIPTOS_PATH, FORMULARIOS_PATH


class ProcessedDataframe():

    def __init__(self, df: pd.DataFrame ) -> None:
        self.df = df

    # ---------------------------------------- pre-processing ------------------------------
    @staticmethod
    def concatenate_df() -> pd.DataFrame: 

        df_1 = pd.read_excel(MUNICIPIOS_PATH)
        df_2 = pd.read_excel(INSCRIPTOS_PATH)
        df_3 = pd.read_excel(FORMULARIOS_PATH)


        if len(df_2) != len(df_3):
            raise ValueError(
                f"ficha_inscriptos ({len(df_2)}) and formularios_curso({len(df_3)}))"
                f"have different numbers of rows."
            )
        # Concatenating dataframes by column
        df = pd.concat([df_2, df_3], axis=1)

        if 'municipio' not in df.columns or 'municipio' not in df_1.columns:
            raise ValueError("The 'municipio' column is missing for the merge with municipios")

        df['_municipio_key'] = df['municipio'].astype(str).str.strip().str.casefold()
        municipios = df_1.copy()
        municipios['municipios_key'] = municipios['municipio'].astype(str).strip().str.casefold()

        #df = df.merge(df_1, on='municipio', how='left')
        if not municipios['_municipio_key'].is_unique:
            dup  = municipios.loc[
                municipios['_municipio_key'].duplicate(keep=False), 'municipio'
            ].unique().tolist()
            raise ValueError(
                f"'municipio' in base_municipios is not unique after normalizing"
                f"spaces/capitalization:{dup}."
            )

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

    # --------------------------------------- Calculation of a Missing Attribute (Age)  -----------------------------------------
    @staticmethod
    def calculate_age(df: pd.DataFrame) -> pd.DataFrame:

        df['fecha_de_nacimiento'] = pd.to_datetime(
            df['fecha_de_nacimiento'],
            errors='coerce'
        )

        df['fecha_carga'] = pd.to_datetime(
            df['fecha_carga'],
            errors='coerce'
        )

        # Calculate age by applying `relativeDelta` row by row
        df['edad'] = df.apply(
            lambda row: relativedelta(row['fecha_carga'], row['fecha_de_nacimiento']).years 
                        if pd.notnull(row['fecha_de_nacimiento']) and pd.notnull(row["fecha_carga"]) else pd.NA,
            axis=1
        )
        return df

    