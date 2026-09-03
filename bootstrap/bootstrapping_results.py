from typing import Any

import pandas as pd
import numpy as np

from bootstrap.models import (StatsType, BootstrapStatsBinary, BootstrapStatsCategorical, BootstrapStatsContinuous)

class BootstrapResults:

    def __init__(self) -> None:
        self._data: dict[str, dict[str, list[StatsType]]] = {
            "control": {},
            "treatment": {},
        }

    #  method to add stats for a specific group and column
    def add(self, group:str, column: str, stats: StatsType) -> None:
        if group not in self._data:
            raise ValueError(f"Group '{group}' not found.")
        if column not in self._data[group]:
            self._data[group][column] = []
        self._data[group][column].append(stats)

    # method to extract the bootstrapping distribution according to its field
    def get_distribution(
            self,
            group: str,
            column: str,
            field: str,
            category: str | None = None,
    ) -> np.ndarray:
        if group not in self._data:
            raise ValueError(f"Group '{group}' not found.")
        if column not in self._data[group]:
            raise KeyError(f"Column '{column}' not found in group '{group}'.")

        replicas = self._data[group][column]

        if not replicas:
            return np.array([])

        if category is not None:
            values = [
                getattr(r, "proportions" , {}).get(category, np.nan) for r in replicas

                ]
        else:
            values = [getattr(r, field, np.nan) for r in replicas]

        return np.array(values, dtype=float)

    # Method to calculate percentiles and confidence intervales for a given field and column
    def summarize(self, ci: float = 0.95) -> dict[str, pd.DataFrame]:
        alpha = (1 - ci) / 2
        percentiles = [100 * alpha, 50.0, 100 * (1 - alpha)]

        summary: dict[str, list[dict[str, Any]]] = {"control": [], "treatment": []}

        for group in ("control", "treatment"):
            for col, replicas in self._data[group].items():
                if not replicas:
                    continue

                first = replicas[0]

                # ------- Continuous and Binary Variables -------
                if isinstance(first, (BootstrapStatsContinuous, BootstrapStatsBinary)):
                    for field in ("mean", "std", "var"):
                       dist = self.get_distribution(group, col, field)
                       if len(dist) == 0 or np.all(np.isnan(dist)):
                            continue
                       q_low, q_med, q_high = np.nanpercentile(dist, percentiles)
                       summary[group].append({
                           "column": col,
                           "variable_type": first.__class__.__name__,
                           "statistic": field,
                           "mean_bootstrap": float(np.nanmean(dist)),
                           "median_bootstrap": float(q_med),
                           f"ci_lower_{int(ci*100)}": float(q_low),
                           f"ci_upper_{int(ci*100)}": float(q_high),
                           "std_bootstrap": float(np.nanstd(dist, ddof=1)),
                           "n_replicas": len(dist),                        
                        })

                # ------- Categorical Variables -------
                elif isinstance(first, BootstrapStatsCategorical):
                    all_cats = set()
                    for r in replicas:
                        all_cats.update(getattr(r, "proportions", {}).keys())

                    for cat in sorted(all_cats):
                        dist = self.get_distribution(group, col, "proportions", category=cat)
                        if len(dist) == 0 or np.all(np.isnan(dist)):
                            continue
                        q_low, q_med, q_high = np.nanpercentile(dist, percentiles)
                        summary[group].append({
                            "column": col,
                            "variable_type": "BootstrapStatsCategorical",
                            "statistic": f"proportion_{cat}",
                            "mean_bootstrap": float(np.nanmean(dist)),
                            "median_bootstrap": float(q_med),
                            f"ci_lower_{int(ci*100)}": float(q_low),
                            f"ci_upper_{int(ci*100)}": float(q_high),
                            "std_bootstrap": float(np.nanstd(dist, ddof=1)),
                            "n_replicas": len(dist),
                        })
        return{
            "control": pd.DataFrame(summary["control"]),
            "treatment": pd.DataFrame(summary["treatment"]),
        }
    