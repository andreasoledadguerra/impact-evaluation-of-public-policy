import pandas as pd
import numpy as np

from dateutil.relativedelta import relativedelta



# ---------------------------------------- pre-procesamiento ------------------------------
def concatenate_df(df_1:pd.DataFrame, df_2: pd.DataFrame, df_3: pd.DataFrame) -> pd.DataFrame: 
    # Descargamos el dataframe con información de los municipios, los inscriptos al programa y los formularios completos por dichos inscriptos
    df_1= pd.read_excel("base_municipios.xlsx")
    df_2 = pd.read_excel("ficha_inscriptos.xlsx")
    df_3= pd.read_excel("formularios_curso.xlsx")

    # Concatenamos dataframes por columna
    df = pd.concat([df_1, df_2, df_3], axis=1)

    # Eliminamos columnas prescindibles
    df.drop(['municipio'], axis=1, inplace=True)
    return df

# --------------------------------------- Filtración ------------------------------------------



# Filtramos solo los inscriptos en etapa 1
formularios_estudio = df_evaluate[df_evaluate['etapa_inscripcion'] == 1 ]

#Filtramos solo los inscriptos en estado solicitud_adjudicada ó solicitud_elegible_rechazadas_por_excedente 
formularios_estudio[formularios_estudio['state'] == 'solicitud_adjudicada']
formularios_estudio[formularios_estudio['state'] =='solicitud_elegible_rechazadas_por_excedente']

# Asignamos variable al filtro de los inscriptos en estado solicitud_adjudicada ó solicitud_elegible_rechazadas_por_excedente
filtro = (formularios_estudio['state'] == 'solicitud_adjudicada') | \
         (formularios_estudio['state'] == 'solicitud_elegible_rechazadas_por_excedente')

# Creamos el nuevo dataframe aplicando el filtro
formularios_estudio = formularios_estudio[filtro]


# --------------------------- Cálculo de atributo faltante (edad) -----------------------------

# Como los valores de cada columna son de distinto tipo de dato, transformamos 'fecha_de_nacimiento' y 'fecha de_carga'
formularios_estudio.loc['fecha_de_nacimiento'] = pd.to_datetime(
    formularios_estudio['fecha_de_nacimiento'],
    errors='coerce'
)

formularios_estudio.loc['fecha_carga'] = pd.to_datetime(
    formularios_estudio['fecha_carga'],
    errors='coerce'
)

#TODO:ver función lambda
# Calcular edad aplicando relativedelta fila a fila
formularios_estudio['edad'] = formularios_estudio.apply(
    lambda row: relativedelta(row['fecha_carga'], row['fecha_de_nacimiento']).years 
                if pd.notnull(row['fecha_de_nacimiento']) else pd.NA,
    axis=1
)

# --------------------------......... Cálculo directo de media -----------------------------------------

vuln = float(round(formularios_estudio['escenario_vulnerabilidad_social'].mean(skipna=True), 1))
#paredes_ext_rev = float(round(formularios_estudio['paredes_ext_revocadas'].mean(skipna=True), 1))
paredes_ext_rev = round(formularios_estudio['paredes_ext_revocadas'].mean(skipna=True), 1)



# ---