RANDOM_STATE = 42

SAMPLE_SIZE = 1000 


NUM_COLUMNS = ['ingreso_anual_hogar', # FORMULARIOS_PATH
                'edad', # FORMULARIOS_PATH, calculated in preprocessing.py using fecha_de_nacimiento and fecha_carga
                'personas_por_ambiente' # FORMULARIOS_PATH
]

CAT_CONDITIONS = {
    'sexo_dni': ['F', 'M'], # FORMULARIOS_PATH
    'relacion_de_parentezco_con_jefe_del_hogar': ['Soy jefa(e)'], # FORMULARIOS_PATH
    'conurbano_interior': ['Conurbano'] # MUNICIPIOS_PATH
}

SPC_COLUMNS = ['escenario_vulnerabilidad_social', # FORMULARIOS_PATH
               'paredes_ext_revocadas' # FORMULARIOS_PATH
]