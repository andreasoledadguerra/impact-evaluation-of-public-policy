import pandas as pd


# Descargamos el dataframe con información de los municipios, los inscriptos al programa y los formularios completos por dichos inscriptos
df_muni = pd.read_excel("base_municipios.xlsx")
df_insc = pd.read_excel("ficha_inscriptos.xlsx")
df_form = pd.read_excel("formularios_curso.xlsx")


# Concatenamos dataframes por columna
df_evaluate = pd.concat([df_muni, df_insc, df_form], axis=1)

# Eliminamos columnas prescindibles, como 'municipio'
df_evaluate.drop(['municipio'], axis=1, inplace=True)