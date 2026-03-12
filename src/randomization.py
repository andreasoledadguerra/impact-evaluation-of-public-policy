import pandas as pd
import numpy as np

from src.preprocessing import ProcessedDataframe



# Initialize processed dataframe

process_df = ProcessedDataframe()

# ------------------------------------ Filtro inicial de candidatos por grupo ----------------------------

## Se agrupa en 'Tratamiento' si se cumple 'solicitud_adjudicada', y 'control', en caso contrario
#formularios_estudio['grupo'] = np.where( formularios_estudio['state'] == 'solicitud_adjudicada','Tratamiento', 'Control')
#
## Guardar extracción de datos en "Control" o "Tratamiento"
#grupo_control = (formularios_estudio['grupo']) == 'Control' # es una serie que devuelve booleanos
#grupo_tratamiento = (formularios_estudio['grupo']) == 'Tratamiento' # idem
#
## A cada grupo le damos estructura de dataframe nuevo
#df_control = formularios_estudio[grupo_control]
#df_tratamiento = formularios_estudio[grupo_tratamiento]
#
## Se eliminan columnas innecesarias en ambos dataframes
#df_control_clean = df_control.drop(columns=[
#    'codigo_municipio', 'codigo_region', 'nombre_region', 'codigo_area',
#    'nombre_area', 'seccion_electoral',
#    'superficie(km2)', 'intendente', 'partido_politico_actual', 
#    'poblacion_censo_2010', 'poblacion_censo_2022'
#])
#
#df_tratamiento_clean = df_tratamiento.drop(columns=[
#    'codigo_municipio', 'codigo_region', 'nombre_region', 'codigo_area',
#    'nombre_area', 'seccion_electoral',
#    'superficie(km2)', 'intendente', 'partido_politico_actual', 
#    'poblacion_censo_2010', 'poblacion_censo_2022'
#])