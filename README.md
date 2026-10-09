# Impact Evaluation of Public Policy 📊

A modular Python pipeline for evaluating the causal impact of public policy interventions using randomized experimental design, statistical analysis, and reproducible data workflows.

> Although built around a public policy campaign, **the methodology is fully transferable** to commercial settings: A/B testing, customer segmentation, product intervention analysis, and more.

---

## Project Structure

```
IMPACT-EVALUATION-OF-PUBLIC-POLICY/
│
├──main.py                     # Pipelin entry point (stages 1-9)
├── config.py                  # Centralized paths (raw sources, final outputs)
├── constants.py               # Domain contants (column names, thresholds, sample size)
├── experiment.py              # Experiment orchestration ------------x
├── models.py                  # Statistical models ------------------x

│
├── bootstrap/                 # Bootstrapping modules
│   ├── __init__.py
│   └── bootstrapping_application.py # Low-level bootstrap sampling (numpy)
│   └── bootstrapping_experiment.py  # BootstrapExperiment - orchestrates sampling + stats + SMD
│   ├── bootrstrapping_results.py    # BootstrapResults - accumulates stats across replicas, percentiles CIs
│   ├── column_registry.py           # ColumnRegistry - column -> variable type (continuos / binary / categorical)
│   └── models.py                    # Pydantic models for bootstrap statistics
│   └── traceability.py              # BootstrapTraceability - per-replica seeds/scores and winner tracking

├── representativity/         
│   └── __init__.py
│   └── representativeness.py        # RepresentativenessCalculator -  sample vs. population coefficient        
│   └── smd.py                 # SMDCalculator - Standardized Mean Diffference by variable type
|
├── src/
│   ├── __init__.py
│   ├── preprocessing.py       # Data cleaning and transformation
│   ├── randomization.py       # Simple random sampling (SRS) per group
│   ├── population.py          # population's statistics
│   ├── sampleanalysis.py      # SampleAnalysis class - descriptive stats on samples
│   ├── visualization.py       # Plots and charts-----------------X
│   └── reporting.py           # Report and export generation-----X
│   └── utils.py               # Pure utility functions (mean, std, proportions)
|
├── visualizations/
│   ├── group_comparison.py    # GroupComparisonPlotter - population  vs. control vs. treatment plots
│   ├── config_plot.py         # PLotconstants (colors, figure sizes, DPI)

├── data/
│   ├── raw/                   # Original source files — never modified
│   ├── processed/             # Output of preprocessing (Parquet)
│   └── final/                 # Group-split data ready for analysis
│         ├── tables/          # Summary tables (.xlsx) and best-replica samples (.parquet)
│         ├── distributions/   # Distribution plots (.png)
│         └── traceability/    # Per-run traceability files (kept across runs)
├── notebooks/
│   └── impact_evaluation_policy.ipynb   # EDA and exploratory analysis
│
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## Pipeline orchestration entry point - main.py

Workflow:
    0. Preprocessing: oad the thre sources, merge, filter (registration stage 1, adjudicated or elegible-but-rejected-for-surplus application),compute age
    1. Statistical summary of the population
    2. Group assignment (control / treatment) + simple random sampling (SRS) of SAMPLE_SIZE per group
    3. Descriptive statistics of the SRS samples
    4. Representativeness of the SRS samples vs. the population 
    5. Bootstrapping on the SRS samples (n_replicas); per-replica statistics, representativeness, SMD and traceability; selection of the best replica per group
    6. Representativeness of the bootstrap replicas (percentile intervals)
    7. SMD balance between control and treatment (summarize across replicas)
    8. Distribution plots (population vs. control vs. treatment)
    9. Export of results


---

Group assignment: treatment = state == "solicitud_adjudicada"; control = the remaining applications that passed the filter.

## Statistical Methods

| Method | Purpose |
|---|---|
| Simple Random Sampling (SRS) | Draw representative samples from each group |
| Mean & Standard Deviation | Descriptive statistics per variable |
| Standardized Mean Difference (SMD) | Balance check between control and treatment |
| Proportions by category | Distribution of categorical variables per group |
| Representativeness coefficient| 1 - relative error of the samplemean/proportin vs. the population |
| Bootstrap resampling | Variability of every statistic across n_bootstrap replicas (default 10000); percentile confidence intervals |
| Standardized Mean Difference (SMD) | Balancecheck between control and treatment |
| Replica traceability | Seed and scores per replica, so anyreplica (including the selected one) can be regenerated |


**SMD**
SMD = (mean_treatment - mean_control) / pooled SD, with the pooled SD defines as sqrt((var_1 + var_2) / 2).

- Continuous / binary variables: Coen's d with the pooled SD above.
- Categorical variables: one SMD per category (dummy coding, last category as reference), summarized as the largest |SMD|. The sign of that value refers to the ingle category that produced it, so judge balance by magnitud.
- Per replica: the SMD is computed on every bootstrap replica and summarized across replicas (mean, median, 95% percentile interval). The balance label is ased on the meand SMD.

  **SMD interpretation:**

  | abs(SMD) | Balance |
  |---|---|
  | < 0.1 | ✅ Excellent — groups are comparable |
  | 0.1 – 0.25 | ⚠️ Acceptable — moderate difference |
  | > 0.25 | ❌ Imbalanced — groups differ significantly |


## Setup

```bash
# Clone the repository
git clone https://github.com/andreasoledadguerra/impact-evaluation-of-public-policy.git
cd impact-evaluation-of-public-policy

# Create and activate virtual environment
python -m venv env
source env/bin/activate        # Mac/Linux
env\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## Requirements

```
pandas
numpy
scipy
matplotlib
seaborn
openpyxl
pyarrow
dateutil
```

## License

MIT License — see `LICENSE` for details.