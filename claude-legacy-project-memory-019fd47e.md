**Purpose & context**

Andy is working on a Python-based impact evaluation of a public policy project, implementing a full bootstrap sampling and representativeness analysis pipeline for an experimental design with three groups: Población (population), Control, and Treatment. The project's goal is to assess group balance and representativeness across variable types. Andy works as a senior Python developer and engages Claude as a senior Python auditor with scientific criteria.

**Variable taxonomy:**
- `NUM_COLUMNS`: continuous variables (`ingreso_anual_hogar`, `edad`, `personas_por_ambiente`)
- `CAT_CONDITIONS`: categorical variables (`sexo_dni`, `relación_de_parentezco_con_jefe_del_hogar`, `conurbano_interior`) defined as a dict of column-to-allowed-categories mappings
- `SPC_COLUMNS`: binary/boolean variables (`escenario_vulnerabilidad_social`, `paredes_ext_revocadas`)

**Data sources:** `ficha_inscriptos.xlsx` + `formularios_curso.xlsx` (concatenated positionally, same row count — risk accepted explicitly), merged with `base_municipios.xlsx` via `pd.merge(on="municipio", how="left")`.

**Key stack:** Python, Pydantic v2, NumPy, pandas, pathlib.

---

**Current state**

The pipeline has been substantially built and audited across ~12 files. Recent sessions focused on the visualization layer and several architectural refinements:

- **`GroupComparisonPlotter`** (`visualizations/group_comparison.py`): Unified class refactoring `distributions.py` and `proportions.py`, covering KDE plots (`NUM_COLUMNS`) and grouped bar charts (`SPC_COLUMNS`, `CAT_CONDITIONS`). Visual config centralized in `visualizations/config.py`.
- **`plot_variable_proportions()`**: Designed as a mirror of `plot_variable_distributions()`, displaying proportion comparisons across the three groups for binary and categorical columns.
- **`experiment.registry` property**: `BootstrapExperiment` now exposes `registry` as a read-only property so downstream consumers like `GroupComparisonPlotter` reuse the same `ColumnRegistry` instance.
- **Rounding bug fix confirmed:** `GroupSummary._calculate()` in `schema.py` was rounding each proportion to 4 decimal places before summing, causing Pydantic's `validate_proportions` validator (`atol=1e-5`) to reject legitimate partitions. Reproduced concretely (n=6, counts 1/1/4) and fixed.
- **Categorical tautology bug fixed** across `bootstrapping_experiment.py`, `group_summary.py`, and `schema.py`: proportions now computed over the full series with a residual `"otros"` bucket rather than filtering to allowed categories first.

**Pending:** SMD balance calculation between control and treatment across N bootstrap replicas is left commented in `bootstrapping_experiment.py` — Andy has not yet decided how to handle it.

---

**On the horizon**

- Resolving the SMD control-vs-treatment balance calculation design across N bootstrap replicas.
- Continued expansion and testing of the visualization layer.

---

**Key learnings & principles**

- **Categorical proportions must be computed over the full series** — filtering to allowed categories before `value_counts(normalize=True)` creates a tautology (always sums to 1.0 for non-exhaustive conditions). A residual `"otros"` bucket is the correct fix.
- **Round after aggregation, not before** — rounding individual proportions before summing introduces cumulative error that can fail strict tolerance validators.
- **Population baseline precomputed once** before the N-replica bootstrap loop to avoid redundant `.mean()` calls on large DataFrames.
- **Best sample selection** uses `abs(coef_representativeness - 1)` as error metric, ranked by average percentile across variables (percentile-normalized to prevent high-variance variables from dominating), with separate rankings for control and treatment.
- **`ColumnRegistry` is an internal dependency** of `BootstrapExperiment`, not injected — downstream consumers access it via the read-only `registry` property.
- **`SampleAnalysis` stays separate from `GroupSummary`/`SubGroupSummary`**: the former returns DataFrames for export; the latter returns Pydantic-typed objects.
- **`SMDCalculator`** operates on `BootstrapStats*` objects with `@staticmethod` methods only (no constructor); **`RepresentativenessCalculator`** is architecturally separate because it compares each group against population (not groups against each other) and uses single population std rather than pooled std.

---

**Approach & patterns**

- Andy audits by pasting relevant files directly into chat — no connectors or Drive integration.
- Claude reconstructs a minimal stub environment for testing: stub files for dependencies with minimal implementations sufficient to instantiate the class under test, then runs the actual file against those stubs to catch real integration bugs without needing the full project.
- **All code changes must be delivered as downloadable files** (not inline code blocks), with the exact file path shown for each file. Files output to `/mnt/user-data/outputs/` mirroring real project folder structure, then presented with `present_files`.
- The real folder name is `visualizations/` (plural) — not `visualization/`.
- The correct file name is `bootstrapping_results.py` (not `bootstrap_results.py`).

**Key architectural patterns:**
- Pydantic v2 discriminated unions: `StatsType = BootstrapStatsContinuous | BootstrapStatsBinary | BootstrapStatsCategorical`, discriminated by `dtype_kind: Literal[...]`
- `numpy.random.SeedSequence.spawn()` for reproducible per-replica randomness across N bootstrap iterations
- `config.py` with `pathlib.Path` for all file paths
- `_clear_output_dir()` in `main.py` deletes existing `.xlsx`/`.parquet` files before each export run

---

**Tools & resources**

- Python, Pydantic v2, NumPy, pandas, pathlib, matplotlib (for visualizations)
- Input data: `ficha_inscriptos.xlsx`, `formularios_curso.xlsx`, `base_municipios.xlsx`
- Output formats: `.xlsx`, `.parquet`