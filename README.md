# Impact Evaluation of Public Policy 📊

A modular Python pipeline for evaluating the causal impact of public policy interventions using randomized experimental design, statistical analysis, and reproducible data workflows.

> Although built around a public policy campaign, **the methodology is fully transferable** to commercial settings: A/B testing, customer segmentation, product intervention analysis, and more.

---

## Project Structure

```
IMPACT-EVALUATION-OF-PUBLIC-POLICY/
│
├── config.py                  # Centralized paths and parameters
├── experiment.py              # Experiment orchestration
├── models.py                  # Statistical models
│
├── bootstrap/                 # Bootstrapping modules
│   ├── __init__.py
│   └── bootstrapping.py
│
├── data/
│   ├── raw/                   # Original source files — never modified
│   ├── processed/             # Output of preprocessing (Parquet)
│   └── final/                 # Group-split data ready for analysis
│
├── notebooks/
│   └── impact_evaluation_policy.ipynb   # EDA and exploratory analysis
│
├── representativity/          # Balance checks and SMD analysis
│
├── src/
│   ├── __init__.py
│   ├── preprocessing.py       # Data cleaning and transformation
│   ├── group_splitting.py     # Control / treatment group separation
│   ├── randomization.py       # Simple random sampling (SRS)
│   ├── analysis.py            # Statistical and econometric analysis
│   ├── visualization.py       # Plots and charts
│   └── reporting.py           # Report and export generation
│
├── .gitignore
├── LICENSE
└── requirements.txt
```

---

## Pipeline Overview

```
Raw Data
   │
   ▼
preprocessing.py       → Cleans, imputes, transforms → saves to data/processed/
   │
   ▼
group_splitting.py     → Separates control and treatment groups → saves to data/final/
   │
   ▼
randomization.py       → Draws simple random samples (n=1000) from each group
   │
   ▼
analysis.py            → Computes descriptive stats, SMD balance checks
   │
   ▼
reporting.py           → Exports results to Excel / visualizations
```

Each stage is **independent and testable** — outputs are persisted as Parquet files between runs, so stages can be executed separately without rerunning the full pipeline.

---

## Key Design Decisions

**Single Responsibility per module** — each `.py` file has one clearly defined role. Changing the group assignment logic never touches preprocessing, and vice versa.

**Parquet over CSV** — intermediate data is stored in Parquet format to preserve column types (dates, categoricals, booleans) across pipeline runs without manual re-casting.

**Centralized configuration** — all file paths and parameters live in `config.py` at the project root. No hardcoded paths inside modules.

**Immutable raw data** — `data/raw/` is never written to. All transformations produce new files in `data/processed/` or `data/final/`.

**Privacy by convention** — the `_` prefix marks internal helper functions (e.g. `_calcular_media_std`) that are implementation details, not part of the public module API.

---

## Statistical Methods

| Method | Purpose |
|---|---|
| Simple Random Sampling (SRS) | Draw representative samples from each group |
| Mean & Standard Deviation | Descriptive statistics per variable |
| Standardized Mean Difference (SMD) | Balance check between control and treatment |
| Proportions by category | Distribution of categorical variables per group |
| Bootstrap resampling | Confidence interval estimation |

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