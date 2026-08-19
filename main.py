
import pandas as pd

from config import FINAL_DATA_PATH
from src.preprocessing import ProcessedDataframe
from src.randomization import randomization, generate_samples_first, compute_sample_statistics_first
from src.sampleanalysis import SampleAnalysis
from bootstrap.bootstrapping_experiment import BootstrapExperiment
from constants import NUM_COLUMNS, CAT_CONDITIONS, SPC_COLUMNS

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
    #print("Columnas después de concatenar:", raw_df.columns.tolist())
    #print("¿Está conurbano_interior?", 'conurbano_interior' in raw_df.columns)
    #print("¿Está relación...?", 'relacion_de_parentezco_con_jefe_del_hogar' in raw_df.columns)


    filtered_df = ProcessedDataframe.filter_df(raw_df)
    #print("Columnas después de filtrar:", filtered_df.columns.tolist())


    aged_df = ProcessedDataframe.calculate_age(filtered_df)
    processed_df = ProcessedDataframe(aged_df)
    #print("Columnas después de calcular edad:", aged_df.columns.tolist())


    # -----------------------------------------------------------------
    # 1. Grouping + simple random sampling (SRS)
    # -----------------------------------------------------------------
    df_control, df_treatment = randomization(processed_df.df)
    srs_c, srs_t = generate_samples_first(df_control, df_treatment, random_state=RANDOM_STATE)
    

    # -----------------------------------------------------------------
    # 2. Bootstrapping on SRS Samples
    # -----------------------------------------------------------------
    # Each column type requires a different calculation path:
    #   - NUM_COLUMNS    -> continuous: mean + std + var + cv
    #                       (BootstrapStatsContinuous)
    #   - CAT_CONDITIONS -> specific condition by (column, value), e.g.
    #                       (‘relacion_de_parentezco_con jefe_del hogar'’,
    #                       ‘'Soy jefa(e)’). This is NOT exhaustive per column,
    #                       so it should be resolved as
    #                       BootstrapStatsBinary for each condition
    #                       (proportion + p*(1-p)), not as
    #                       BootstrapStatsCategorical—that model requires
    #                       sum(proportions) == 1.0.
    #   - SPC_COLUMNS    -> coded numerical / ordinal: rounded mean,
    #                       no var/std 

    for col in CAT_CONDITIONS:
        print(f"\nColumna: {col}")
        print(f"  Control: nulos={df_control[col].isna().sum()} / total={len(df_control)}")
        print(f"  Tratamiento: nulos={df_treatment[col].isna().sum()} / total={len(df_treatment)}")
        print(f"  Categorías en control: {df_control[col].dropna().unique()}")
        print(f"  Categorías en tratamiento: {df_treatment[col].dropna().unique()}")

        
    experiment = BootstrapExperiment(
        data=(srs_c, srs_t),
        num_columns=NUM_COLUMNS,
        cat_conditions=CAT_CONDITIONS,
        spc_columns=SPC_COLUMNS,
        random_state=RANDOM_STATE,
    )


    bootstrap_c = experiment.bootstrap_c
    bootstrap_t = experiment.bootstrap_t
    smd_summary = experiment.smd_summary  # Control vs. Treatment Comparison

    # -----------------------------------------------------------------
    # 3. Representativeness coefficient of the sample vs. the population
    # -----------------------------------------------------------------
    rep_coef_iah = calculate_rep_coef(
        processed_df=processed_df.df,
        sample=(srs_c, srs_t),
        column="ingreso_anual_hogar",
    )

    # -----------------------------------------------------------------
    # 4. Final Descriptive Statistics
    # -----------------------------------------------------------------
    sample_analysis = compute_sample_statistics_first((srs_c, srs_t))
    media_std = sample_analysis.sample_media_std()
    media_condition = sample_analysis.sample_media_condition()
    media_round = sample_analysis.calculate_media_round()

    # -----------------------------------------------------------------
    # 5. Exporting Results
    # -----------------------------------------------------------------
    FINAL_DATA_PATH.mkdir(parents=True, exist_ok=True)
    
    smd_summary.to_excel(FINAL_DATA_PATH / "smd_summary.xlsx", index=False)
    bootstrap_c.to_parquet(FINAL_DATA_PATH / "bootstrap_control.parquet", index=False)
    bootstrap_t.to_parquet(FINAL_DATA_PATH / "bootstrap_treatment.parquet", index=False)

    results = {
        "bootstrap_c": bootstrap_c,
        "bootstrap_t": bootstrap_t,
        "smd_summary": smd_summary,
        "rep_coef_iah": rep_coef_iah,
        "sample_analysis": sample_analysis,
        "media_std": media_std,
        "media_condition": media_condition,
        "media_round": media_round,
    }

    return results
    
    
if __name__ == "__main__":
    main()
 
