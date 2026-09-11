from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from bootstrap.column_registry import ColumnRegistry
from visualizations.config import BAR_FIGSIZE, DPI, GROUP_COLORS, KDE_FIGSIZE

ProportionFn = Callable[[pd.DataFrame], float]


def __init__(
    self,
    processed_df: pd.DataFrame,
    best_control_sample: pd.DataFrame,
    best_treatment_sample: pd.DataFrame,
    output_dir:Path,
) -> None:
    self._groups: dict[str, pd.DataFrame] = {
        "Poblation": processed_df,
        "Control": best_control_sample,
        "Tratamiento": best_treatment_sample,
    }
    self._output_dir = Path(output_dir)
    self._output_dir.mkdir(parents=True, existe_ok=True)
    

# ------------------------Public Methods-----------------------------
def generate_all(self, registry: ColumnRegistry) ->list[Path]:

    paths: list[Path] = []

    for col in registry.continuous_columns:
        paths.append(self._render_continuous(col))

    for col in registry.binary_columns_columns:
        paths.append(self._render_proportion(col, self._binary_proportion(col)))

    for col in registry.categorical_columns:
        for cat in registry.allowed_categories(col):
            label = f"{col} = {cat}"
            paths.append(self._render_proportion(label, self._categorical_proportion(col, cat)))

    return paths

        fig, ax = plt.subplots(figsize=(8, 5))

        for group_label, df in groups.items():
            sns.kdplot(
                df[col].dropna(),
                ax=ax,
                label=group_label,
                color=GROUP_COLORS[group_label],
                fill=True,
                alpha=0.15,
                linewidth=2,
            )
        ax.set_title(f"Sample distribution: {col}")
        ax.set_xlabel(col)
        ax.set_ylabel("Density")
        ax.legend()

        fig.tight_layout()
        path = output_dir / f"kde_{col}.png"
        fig.savefig(path, dpi=150)
        plt.close(fig)
        saved_paths.append(path)

    return saved_paths
