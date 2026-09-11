from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from bootstrap.column_registry import ColumnRegistry
from visualizations.config import BAR_FIGSIZE, DPI, GROUP_COLORS, KDE_FIGSIZE


def plot_variable_distributions(
        processed_df: pd.DataFrame,
        best_control_sample: pd.DataFrame,
        best_treatment_sample: pd.DataFrame,
        columns: list[str],
        output_dir:Path,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_paths: list[Path] = []

    groups = {
        "Poblation": processed_df,
        "Control": best_control_sample,
        "Treatment":best_treatment_sample ,
    }

    for col in columns:
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
