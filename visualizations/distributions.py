from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

GROUP_COLORS = {
    "Poblation": "#4C72B0",
    "Control": "#55A868",
    "Treatment": "#C44E52",
}

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
