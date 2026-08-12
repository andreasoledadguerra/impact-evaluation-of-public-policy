# Impact Evaluation of Public Policy 📊

A modular Python pipeline for evaluating the causal impact of public policy interventions using randomized experimental design, statistical analysis, and reproducible data workflows.

> Although built around a public policy campaign, **the methodology is fully transferable** to commercial settings: A/B testing, customer segmentation, product intervention analysis, and more.

---

## Project Structure

```
IMPACT-EVALUATION-OF-PUBLIC-POLICY/
│
├── config.py                  # Centralized paths and parameters
├── constants.py               # Domain contants (column names, thresholds, sample size)
├── experiment.py              # Experiment orchestration ------------x
├── models.py                  # Statistical models ------------------x

│
├── bootstrap/                 # Bootstrapping modules
│   ├── __init__.py
│   └── bootstrapping_application.py # Low-level bootstrap sampling (numpy)
│   └── bootstrapping_experiment.py  # BootstrapExperiment - orchestrates sampling + stats + SMD
│   └── models.py # Pydantic models for bootstrap statistics
│
├── representativity/         
│   └── __init__.py
│   └── smd.py                 # SMDCalculator - Standardized Mean Diffference by variable type
|
├── src/
│   ├── __init__.py
│   ├── preprocessing.py       # Data cleaning and transformation
│   ├── randomization.py       # Simple random sampling (SRS) per group
│   ├── sampleanalysis.py      # SampleAnalysis class - descriptive stats on samples
│   ├── visualization.py       # Plots and charts-----------------X
│   └── reporting.py           # Report and export generation-----X
│   └── utils.py               # Pure utility functions (mean, std, proportions)
|
├── data/
│   ├── raw/                   # Original source files — never modified
│   ├── processed/             # Output of preprocessing (Parquet)
│   └── final/                 # Group-split data ready for analysis
│
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
    1. Loading processed data
    2. Initial sample extraction (SRS) by group + descriptive statistics
    3. Bootstrapping by group (control / treatment)
    4. Calculation of SMD to assess balance between groups
    5. Sample representativeness coefficient vs. population
    6. Final descriptive analysis of the samples
    7. Export of results


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