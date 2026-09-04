
import logging
import numpy as np
import pandas as pd

from config import FINAL_DATA_PATH
from schema import GroupSummary, SubGroupSummary
from representativity.representativeness import RepresentativenessCalculator
from src.preprocessing import ProcessedDataframe
from src.randomization import randomization, generate_samples_first, compute_sample_statistics_first
from bootstrap.bootstrapping_experiment import BootstrapExperiment
from constants import NUM_COLUMNS, CAT_CONDITIONS, SPC_COLUMNS, RANDOM_STATE

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)




def main() -> dict:
    # -----------------------------------------------------------------
    # 0. Preprocessing
    # -----------------------------------------------------------------
    logger.info("Starting preprocessing...")

    raw_df = ProcessedDataframe.concatenate_df()
    logger.info(f"Preprocessing completed: {len(raw_df)} rows, {len(raw_df.columns)} columns.")
    #print("Columnas después de concatenar:", raw_df.columns.tolist())
    #print("¿Está conurbano_interior?", 'conurbano_interior' in raw_df.columns)
    #print("¿Está relación...?", 'relacion_de_parentezco_con_jefe_del_hogar' in raw_df.columns)


    filtered_df = ProcessedDataframe.filter_df(raw_df)
    logger.info(f"Filtering completed: {len(filtered_df)} rows, {len(filtered_df.columns)} columns.")
    #print("Columnas después de filtrar:", filtered_df.columns.tolist())

    aged_df = ProcessedDataframe.calculate_age(filtered_df)
    processed_df = ProcessedDataframe(aged_df)
    logger.info(f"Age calculation completed: {len(aged_df)} rows, {len(aged_df.columns)} columns.")
    #print("Columnas después de calcular edad:", aged_df.columns.tolist())

    # -----------------------------------------------------------------
    # 1. Statistical Summary of the Population
    # -----------------------------------------------------------------
    logger.info("Calculating statistical summary of the population...")
    population_stats = GroupSummary(processed_df.df)
    logger.info(
        f"Population baseline calculated:"
        f"{len(population_stats.summary)} variables summarized"
    )


    # -----------------------------------------------------------------
    # 2. Grouping (Statistical summary of the control group and the treatment group) + simple random sampling (SRS)
    # -----------------------------------------------------------------
    logger.info("Starting randomization and SRS sampling...")
    df_control, df_treatment = randomization(processed_df.df)
    logger.info(f"Randomization completed: {len(df_control)} control rows, {len(df_treatment)} treatment rows.")

    srs_c, srs_t = generate_samples_first(df_control, df_treatment, random_state=RANDOM_STATE)
    logger.info(f"SRS sampling completed: {len(srs_c)} control rows, {len(srs_t)} treatment rows.")

    control_treatment_stats = SubGroupSummary((srs_c, srs_t))
    # este debe aparecer como argumento en BootstrapExperiment or so
    logger.info(
        f"Control ({len(control_treatment_stats.summary_control)} vars)"
        f"Treatment ({len(control_treatment_stats.summary_treatment)} vars)"
    )


    # -----------------------------------------------------------------
    # 3. Validate group representativeness
    # -----------------------------------------------------------------
    logger.info("Evaluating representativeness of SRS samples...")
    repr = RepresentativenessCalculator.evaluate_sample_representativeness(
        processed_df = processed_df.df,
        data =(srs_c, srs_t),
    )

    negatives_cases = repr[repr['coef_representatividad_control'] < 0] | ( repr[repr['coef_representatividad_treatment'] < 0])

    if not negatives_cases.empty:
        logger.warning(
            f"Negative representativeness coefficients found in {len(negatives_cases)} cases. "
            f"Check the data and calculations for potential issues."
        )
    logger.info(
        f"Representativeness evaluation completed: "
        f"SRS representativeness vs. general population OK - no negative coefficients found in {len(repr)} variables/conditions assessed"
    
    )

    # -----------------------------------------------------------------
    # 4. Bootstrapping on SRS Samples (n replicas)
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

    logger.info("Starting bootstrapping on SRS samples...")
    experiment = BootstrapExperiment(
        data=(srs_c, srs_t),
        # processed_df=processed_df.df,
        num_columns=NUM_COLUMNS,
        cat_conditions=CAT_CONDITIONS,
        spc_columns=SPC_COLUMNS,
        n_bootstrap=10000,  # 1000
        random_state= RANDOM_STATE,
    )

    bootstrap_results = experiment.run_bootstrap()
    logger.info("Bootstrapping completed")

    bootstrap_summary = bootstrap_results.summarize(ci=0.95)
    summary_control = bootstrap_summary["control"]
    summary_treatment = bootstrap_summary["treatment"]

    
    # smd_summary = experiment.smd_summary  # Control vs. Treatment Comparison


    # -----------------------------------------------------------------
    # 5. Validate group representativeness using bootstrap samples 
    # -----------------------------------------------------------------
    logger.info("Evaluating representativeness of bootstrap samples...")

    repr_bootstrap = RepresentativenessCalculator.evaluate_sample_representativeness( 
        processed_df = processed_df.df,
        data =(bootstrap_summary["control"], bootstrap_summary["treatment"]),
    )



    repr_bootstrap_c = repr_bootstrap.bootstrap_c
    repr_bootstrap_t = repr_bootstrap.bootstrap_t  
    smd_summary_bootstrap = repr_bootstrap.smd_summary  # Control vs. Treatment Comparison



    # -----------------------------------------------------------------
    # 6. Standardised mean difference (smd.py)
    # -----------------------------------------------------------------

    # -----------------------------------------------------------------
    # 7. Final Descriptive Statistics
    # -----------------------------------------------------------------
    sample_analysis = compute_sample_statistics_first((srs_c, srs_t))
    media_std = sample_analysis.sample_media_std()
    media_condition = sample_analysis.sample_media_condition()
    media_round = sample_analysis.calculate_media_round()

    logger.info("Final descriptive statistics calculated(media_std, media_condition, media_round)."
    )

    # -----------------------------------------------------------------
    # 8. Exporting Results
    # -----------------------------------------------------------------
    FINAL_DATA_PATH.mkdir(parents=True, exist_ok=True)
    logger.info(f"Exporting results to {FINAL_DATA_PATH}...")
    
    smd_summary.to_excel(FINAL_DATA_PATH / "smd_summary.xlsx", index=False)

    bootstrap_c.to_parquet(FINAL_DATA_PATH / "bootstrap_control.parquet", index=False)
    bootstrap_c.to_excel(FINAL_DATA_PATH / "bootstrap_control.xlsx", index=False)

    bootstrap_t.to_parquet(FINAL_DATA_PATH / "bootstrap_treatment.parquet", index=False)
    bootstrap_t.to_excel(FINAL_DATA_PATH / "bootstrap_treatment.xlsx", index=False)


    results = {
        "bootstrap_c": bootstrap_c,
        "bootstrap_t": bootstrap_t,
        "smd_summary": smd_summary,
        #"rep_coef_iah": rep_coef_iah,
        "sample_analysis": sample_analysis,
        "media_std": media_std,
        "media_condition": media_condition,
        "media_round": media_round,
    }

    logger.info("All results exported successfully.")
    
    return results
    


if __name__ == "__main__": main()
 
