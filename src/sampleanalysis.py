import pandas as pd
from src.utils import calculate_media_std_list, calculate_media_condition
from constants import NUM_COLUMNS, CAT_CONDITIONS, SPC_COLUMNS

class SampleAnalysis:
    
    def __init__(self, df: pd.DataFrame):
        self.df = df

# Muestras aleatorias simples y resumen estadístico por grupo

#Estos métodos se usan en ambos grupos (muestra)
    def sample_media_std(self, columns: list[str]= None) -> pd.DataFrame:
        cols = columns or NUM_COLUMNS
        return calculate_media_std_list(self.df, cols)

    def sample_media_condition(self, conditions: dict = None) -> pd.DataFrame:
        conds = conditions or CAT_CONDITIONS
        return calculate_media_condition(self.df, conds)

#def sample_media_condition(df:pd.DataFrame):
#        dict_condiciones = {
#        'sexo_dni': ['F','M'],
#        'relacion_de_parentezco_con_jefe_del_hogar': ['Soy jefa(e)'],
#        'conurbano_interior': ['Conurbano']
#            }
#
#        sample = calcular_media_condicion(df, dict_condiciones)
#        return sample
#

    def calculate_media_round(self, columns: list[str]= None, decimales: int = 1) -> dict[str, float]:
        cols = columns or SPC_COLUMNS
        return {
            col: float(round(self.df[col].mean(skipna=True), decimales)) 
            for col in cols
        }


#----------------------------este resultado debe sumarse al dataframe-----------------------------------
#def mean_vuln(df:pd.DataFrame):
#    vuln = float(round(df['escenario_vulnerabilidad_social'].mean(skipna=True), 1))
#    return vuln
#
#def mean_ext_rev(df:pd.DataFrame):
#    ext_rev= float(round(df['paredes_ext_revocadas'].mean(skipna=True), 1))
#    return ext_rev
#



