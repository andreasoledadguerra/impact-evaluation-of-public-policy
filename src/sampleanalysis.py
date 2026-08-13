import pandas as pd
from src.utils import calculate_media_std_list, calculate_media_condition
from constants import NUM_COLUMNS, CAT_CONDITIONS, SPC_COLUMNS

class SampleAnalysis:
    
    def __init__(self, df_control: pd.DataFrame, df_treatment: pd.DataFrame):
        self.df_control = df_control
        self.df_treatment = df_treatment

# Muestras aleatorias simples y resumen estadístico por grupo

    def sample_media_std(self, columns: list[str] | None = None) -> pd.DataFrame:
        cols = columns if columns is not None else NUM_COLUMNS
        return self._for_both_groups(calculate_media_std_list, cols)

    def sample_media_condition(self, conditions: dict | None = None) -> pd.DataFrame:
        conds = conditions if conditions is not None else CAT_CONDITIONS
        return self._for_both_groups(calculate_media_condition, conds)

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

    def calculate_media_round(self, columns: list[str] | None = None, decimals: int = 1) -> pd.DataFrame:
        cols = columns if columns is not None else SPC_COLUMNS

        rows = []
        for grupo, df in (("Control", self.df_control), ("Tratamiento", self.df_treatment)):
            fila = {"grupo": grupo}
            fila.update(
                {col: float(round(df[col].mean(skipna=True), decimals)) for col in cols}
            )
            rows.append(fila)
        return pd.DataFrame(rows)


#----------------------------este resultado debe sumarse al dataframe-----------------------------------
#def mean_vuln(df:pd.DataFrame):
#    vuln = float(round(df['escenario_vulnerabilidad_social'].mean(skipna=True), 1))
#    return vuln
#
#def mean_ext_rev(df:pd.DataFrame):
#    ext_rev= float(round(df['paredes_ext_revocadas'].mean(skipna=True), 1))
#    return ext_rev
#--------------------------------------------------------------------------------------------------------

    def _for_both_groups(self, func, arg) -> pd.DataFrame:
        """
        Run `func` on both groups and combine the results into a single
        DataFrame.
        """
        result_c = func(self.df_control, arg).assign(grupo="Control")
        result_t = func(self.df_treatment, arg).assign(grupo="Tratamiento")
        return pd.concat([result_c, result_t], ignore_index=True)
 

