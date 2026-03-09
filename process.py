import pandas as pd



# ---------------------------------------- pre-procesamiento ------------------------------

# Descargamos el dataframe con información de los municipios, los inscriptos al programa y los formularios completos por dichos inscriptos
df_muni = pd.read_excel("base_municipios.xlsx")
df_insc = pd.read_excel("ficha_inscriptos.xlsx")
df_form = pd.read_excel("formularios_curso.xlsx")


# Concatenamos dataframes por columna
df_evaluate = pd.concat([df_muni, df_insc, df_form], axis=1)

# Eliminamos columnas prescindibles, como 'municipio'
df_evaluate.drop(['municipio'], axis=1, inplace=True)

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

