
import pandas as pd
import numpy as np
from src.randomization import randomization, simple_random_sample
from bootstrap.bootstrapping import get_sample_bootstrap, calculate_mean_bootstrap
from src.sampleanalysis import SampleAnalysis  
from src.utils import Stats
from src.preprocessing import ProcessedDataframe
from bootstrap.models import BoostrapStats
from bootstrap.experiment import BootstrapExperiment
from constants import NUM_COLUMNS, CAT_CONDITIONS, SPC_COLUMNS
from representativity.smd import SMDCalculator
from src.randomization import generate_samples_first

sample_analysis = SampleAnalysis()

SAMPLE_SIZE = 1000




# Generar muestras aleatorias del grupo control y tratamiento (paso previo al bootstrapping)

first_sample = generate_sample_first()

#recibe los dataframes de generate_sample_first y hace cálculos estadísticos sobre ciertas variables
first_sample_statistics = compute_sample_statistics_first


# -------------------------------- BOOTSTRAPPING OVER NUM_COLUMNS, CAT_COLUMNS & SPC_COLUMNS-----------------------------------------

columns = [NUM_COLUMNS, CAT_CONDITIONS , SPC_COLUMNS]

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