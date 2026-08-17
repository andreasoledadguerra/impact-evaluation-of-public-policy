
import pandas as pd

from src.preprocessing import ProcessedDataframe
from src.randomization import randomization, generate_samples_first, compute_sample_statistics_first
from src.sampleanalysis import SampleAnalysis
from bootstrap.bootstrapping_experiment import BootstrapExperiment
from constants import NUM_COLUMNS, CAT_CONDITIONS, SPC_COLUMNS

sample_analysis = SampleAnalysis()

RANDOM_STATE = 42

def calculate_rep_coef(
    processed_df: pd.DataFrame,
    sample: tuple[pd.DataFrame, pd.DataFrame],
    column: str,
) -> dict:
    """
    Calculates the representativeness coefficient for each group (control and
    treatment) relative to the original population, for a given column.

    Uses the Standardized Mean Difference (SMD) between the sample mean of each
    group and the population mean, weighted by the population standard deviation.


    Interpretation (Cohen, 1988; Austin, 2009):
        |SMD| < 0.10  -> excellent representativeness
        |SMD| < 0.25  -> acceptable
        |SMD| >= 0.25 -> problematic imbalance

    Args:
        processed_df: DataFrame containing the entire population (post-preprocessing).
        sample: tuple (df_control, df_treatment) containing the extracted samples.
        column: name of the column to evaluate (e.g., “annual_household_income”).

    Returns:
        dict containing population means/standard deviations and the SMD for each group.
    """

    sample_c, sample_t = sample
 
    mean_population = processed_df[column].mean()
    std_population = processed_df[column].std()
 
    mean_c = sample_c[column].mean()
    mean_t = sample_t[column].mean()
 
    # SMD = (media_muestra - media_poblacion) / std_poblacion
    smd_c = (mean_c - mean_population) / std_population
    smd_t = (mean_t - mean_population) / std_population
 
    return {
        "column": column,
        "mean_population": mean_population,
        "std_population": std_population,
        "smd_control": smd_c,
        "smd_treatment": smd_t,
    }

def main() -> dict:
    # -----------------------------------------------------------------
    # 0. Preprocessing
    # -----------------------------------------------------------------
    raw_df = ProcessedDataframe.concatenate_df()
    filtered_df = ProcessedDataframe.filter_df(raw_df)
    aged_df = ProcessedDataframe.calculate_age(filtered_df)
    processed_df = ProcessedDataframe(aged_df)

    # -----------------------------------------------------------------
    # 1. Primera extracción de muestra y cálculo estadístico por grupo
    # -----------------------------------------------------------------
    df_control, df_treatment = generate_samples_first(
        processed_df, sample_size=SAMPLE_SIZE, random_state=RANDOM_STATE
    )

    first_sample_statistics = compute_sample_statistics_first(df_control, df_treatment)

    # -----------------------------------------------------------------
    # 2. Bootstrapping sobre NUM_COLUMNS, CAT_CONDITIONS y SPC_COLUMNS
    # -----------------------------------------------------------------
    # Cada tipo de columna requiere una ruta de cálculo distinta:
    #   - NUM_COLUMNS    -> continua: mean + std + var + cv
    #                       (BootstrapStatsContinuous)
    #   - CAT_CONDITIONS -> condición puntual por (columna, valor), ej.
    #                       ('relación_de_parentezco_con_jefe_del_hogar',
    #                       'Soy jefa(e)'). NO es exhaustivo por columna,
    #                       así que debería resolverse como
    #                       BootstrapStatsBinary por cada condición
    #                       (proporción + p*(1-p)), no como
    #                       BootstrapStatsCategorical — ese modelo exige
    #                       sum(proportions) == 1.0, cosa que una condición
    #                       aislada como 'Soy jefa(e)' no cumple.
    #   - SPC_COLUMNS    -> numérica codificada / ordinal: media redondeada,
    #                       sin var/std (revisar si alguna, ej.
    #                       'paredes_ext_revocadas', es en realidad binaria
    #                       y debería ir por BootstrapStatsBinary también)
    #
    # TODO: confirmar que BootstrapExperiment acepta estos tres parámetros
    # por separado. Si el constructor real solo toma "columns" (como en el
    # borrador original), hay que ampliarlo o instanciar el experimento
    # tres veces, una por tipo de variable.
    experiment = BootstrapExperiment(
        data=(df_control, df_treatment),
        num_columns=NUM_COLUMNS,
        cat_conditions=CAT_CONDITIONS,
        spc_columns=SPC_COLUMNS,
        random_state=RANDOM_STATE,
    )

    # TODO: confirmar si el bootstrap corre al instanciar la clase o si hace
    # falta un método explícito, ej. experiment.run()
    # experiment.run()

    bootstrap_c = experiment.bootstrap_c
    bootstrap_t = experiment.bootstrap_t
    smd_summary = experiment.smd_summary  # balance control vs. tratamiento

    # -----------------------------------------------------------------
    # 3. Coeficiente de representatividad de la muestra vs. población
    #    (ejemplo con "ingreso_anual_hogar" — extensible a otras columnas
    #    iterando sobre NUM_COLUMNS)
    # -----------------------------------------------------------------
    rep_coef_iah = calculate_rep_coef(
        processed_df=processed_df,
        sample=(df_control, df_treatment),
        column="ingreso_anual_hogar",
    )

    # TODO: si SMDCalculator (representativity/smd.py) ya implementa esta
    # lógica de representatividad, calculate_rep_coef() de acá arriba
    # debería llamarlo en vez de reimplementar la fórmula. Evaluar si
    # conviene mover calculate_rep_coef() dentro de SMDCalculator.

    # -----------------------------------------------------------------
    # 4. Estadística descriptiva final sobre las muestras
    # -----------------------------------------------------------------
    # TODO: confirmar si SampleAnalysis recibe los DataFrames en el
    # constructor o en un método aparte (ej. .analyze(df_control))
    sample_analysis = SampleAnalysis()

    # -----------------------------------------------------------------
    # 5. Exportación de resultados
    # -----------------------------------------------------------------
    # TODO: definir rutas reales de salida (ej. data/final/, reports/) y
    # descomentar / adaptar según config.py
    # smd_summary.to_excel(FINAL_DATA_PATH / "smd_summary.xlsx")
    # bootstrap_c.to_parquet(FINAL_DATA_PATH / "bootstrap_control.parquet")
    # bootstrap_t.to_parquet(FINAL_DATA_PATH / "bootstrap_treatment.parquet")

    results = {
        "first_sample_statistics": first_sample_statistics,
        "bootstrap_c": bootstrap_c,
        "bootstrap_t": bootstrap_t,
        "smd_summary": smd_summary,
        "rep_coef_iah": rep_coef_iah,
        "sample_analysis": sample_analysis,
    }

    return results
    
    
if __name__ == "__main__":
    main()
 





# ------------------------------- PRIMERA EXTRACCIÓN DE MUESTRA Y CÁLCULO ESTADÍSTICO POR GRUPO --------------------------------------



# Generar muestras aleatorias del grupo control y tratamiento (paso previo al bootstrapping)
first_sample = generate_samples_first

# Recibe los dataframes de generate_sample_first y hace cálculos estadísticos sobre ciertas variables
first_sample_statistics = compute_sample_statistics_first


# -------------------------------- BOOTSTRAPPING SOBRE NUM_COLUMNS, CAT_COLUMNS & SPC_COLUMNS-----------------------------------------

columns = [NUM_COLUMNS, CAT_CONDITIONS , SPC_COLUMNS]

# Generamos muestras bootstraping, calculamos estadísticas y smd por grupo (por vavriable)
experiment = BootstrapExperiment(
    data = (df_control, df_treatment),
    columns = NUM_COLUMNS,
    random_state= 42
)

# Bootstrap samples
experiment.bootstrap_c # df
experiment.bootstrap_t # df

# Stats per group and column
#experiment.stats_c[].mean
#experiment.stats_t[].var

experiment.smd_summary

# ---- Coeficiente de representatividad de la muestra de cada grupo sobre la variable "iah" -----
# --------- "representativeness coefficient" -------
# Recibe el output de mean_sample_bootstrap()
# Se necesitan: 
# - las medias de la columna de cada grupo
# - las varianzas de la columna de cada grupo
# - utilizar la Diferencia Estandarizada (Standardized Mean Difference — SMD)

# Interpretación:

# - |SMD| < 0.10 → excelente representatividad
# - |SMD| < 0.25 → aceptable
# - |SMD| ≥ 0.25 → desequilibrio problemático (Cohen, 1988; Austin, 2009)




# Calcular la media poblacional del ingreso anual del hogar del dataset original
processed_df = ProcessedDataframe()
calculate_smd = SMDCalculator()

 # mean_COLUMN= processed_df[COLUMN].mean()  # cálculo genérico

mean_population_iah = processed_df['ingreso_anual_hogar'].mean()
std_population_iah = processed_df['ingreso_anual_hogar'].std()
smd_iah = calculate_smd['ingreso_anual_hogar']



#def calculate_rep_coef(processed_df: pd.DataFrame, sample: tuple[pd.DataFrame, pd.DataFrame], COLUMN: str):
#    sample_c, sample_t = sample
#    mean_population_iah = processed_df[COLUMN].mean()
#    rep_coef_mean = 










#median_sample_c = sample_c[COLUMN].median()
#median_sample_t = sample_t[COLUMN].median()