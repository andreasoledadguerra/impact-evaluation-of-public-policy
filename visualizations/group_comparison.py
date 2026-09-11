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

class GroupComparisonPlotter:
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


    # -------------------------------------Public Methods-----------------------------------
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

    # ---------------------------------- Renders ------------------------------------------------
    def _render_continuos(self, col: str) -> Path:
        fig, ax = plt.subplots(figsize=KDE_FIGSIZE)

        for group_label, df in self._groups.items():
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

        return self._save(fig, f"kde_{_slug(col)}")

    def _render_proportion(self, label: str, proportion_fn:ProportionFn) -> Path:
        heights = {g: proportion_fn(df) for g, df in self._group.items()
                   }
        fig, ax = plt.subplots(figsize=BAR_FIGSIZE)
        groups = list(heights.keys())
        values = [heights[g] for g in groups]
        colors = [GROUP_COLORS[g] for g in groups]

        ax.bar(groups, values, color=colors, width=0.6, edgecolor="black", linewidth=0.5)
        ax.set_ylim(0, 1.0)
        ax.set_title(f"`Proportion per group: {label}")
        ax.set_ylabel("Proportion")
        ax.set_xlabel(label)
        ax.axhline(0, color="black", linewidth=0.8)
        for i, v in enumerate(values):
            ax.text(i, v + 0.015, f"{v:.3f}", ha="center", va="bottom", fontsize=9)


        return self._save(fig, f"prop_{_slug(label)}")


# ----------------------------- Calculating Proportions ------------------------------------
@staticmethod
def _binary_proportion(col: str) -> ProportionFn:
        return lambda df: float(df[col].mean())
@staticmethod
def _categorical_proportion(col: str, cat: str) -> ProportionFn:
        return lambda df: float((df[col] == cat).mean())
# ----------------------------- Utilities ----------------------------------------------------
def _save(self, fig, stem: str) -> Path:
    fig.tight_layout()
    path = self._output_dir / f"{stem}.png"
    fig.savefig(path, dpi=DPI)
    plt.close(fig)
    return path
# 
def _slug(text: str) -> str:
        return re.sub(r"^a-zA-Z0-9_]+", "_", text).strip("_")