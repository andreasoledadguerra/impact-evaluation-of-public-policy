import pandas as pd
from constants import NUM_COLUMNS, CAT_CONDITIONS, SPC_COLUMNS
from schema import Mean, Proportions


#@classmethod
def _mean_in_columns(
    processed_df: pd.DataFrame,
    data: tuple[pd.DataFrame, pd.DataFrame],
    column: str,
) -> dict:
    df_control, df_treatment = data

    mean_population = processed_df[column].mean()

    mean_c = df_control[column].mean()
    mean_t = df_treatment[column].mean()

    return {
      "column": column,
      "mean_population": mean_population,
      "mean_control": mean_c,
      "mean_treatment": mean_t,

  }

# p_mean quizá sea una constante

# no toma ni Group(población) ni Subgroup(control/tratamiento)

# Toma processed_data (df) sólo para calcular la media poblacional sobre cada variable
# Luego  tomar df_control, df_treatment (tupla) para calcular la media de cada grupo 

# ver qué puedo usar de utils.py , o directamente usar .mean() dependiendo del tipo de dato

# Método para calcular la media sobre cada grupo dependiendo del tipo de variable:


#def evaluate_repr_c_t(data:tuple[pd.DataFrame, pd.DataFrame], p_mean:float) -> pd.DataFrame:
#    df_control, df_treatment = data
#
#    # Control
#    err_abs_c = abs(media_control - p_mean)
#    err_rel_c = err_abs_c / media_poblacional
#    err_pct_c = err_rel_c * 100
#    coef_repr_c = 1 - err_rel_c
#
#    # Tratamiento
#    err_abs_t = abs(media_tratamiento - media_poblacional)
#    err_rel_t = err_abs_t / media_poblacional
#    err_pct_t = err_rel_t * 100
#    coef_repr_t = 1 - err_rel_t
#
#
#
##función coordinadora, ejemplo
#def evaluate_sample_representativeness(
#    media_control: float,
#    media_tratamiento: float,
#    media_poblacional: float,
#    variable_name: str = "IAH"
#) -> pd.DataFrame:
#    """
#    Calcula errores absoluto, relativo, porcentual y coeficiente de
#    representatividad para grupos control y tratamiento respecto
#    a la media poblacional.
#    """
#    # Control
#    err_abs_c = abs(media_control - media_poblacional)
#    err_rel_c = err_abs_c / media_poblacional
#    err_pct_c = err_rel_c * 100
#    coef_repr_c = 1 - err_rel_c
#
#    # Tratamiento
#    err_abs_t = abs(media_tratamiento - media_poblacional)
#    err_rel_t = err_abs_t / media_poblacional
#    err_pct_t = err_rel_t * 100
#    coef_repr_t = 1 - err_rel_t
#
#    df = pd.DataFrame({
#        "grupo": ["Control", "Tratamiento"],
#        "variable": [variable_name, variable_name],
#        "media_grupo": [media_control, media_tratamiento],
#        "media_poblacional": [media_poblacional, media_poblacional],
#        "error_absoluto": [err_abs_c, err_abs_t],
#        "error_relativo": [err_rel_c, err_rel_t],
#        "error_porcentual": [err_pct_c, err_pct_t],
#        "coef_representatividad": [coef_repr_c, coef_repr_t],
#    })
#
#    return df



