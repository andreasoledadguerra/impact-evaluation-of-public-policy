import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


class ReplicaRecord:

     __slots__ = ("replica_id", "seed", "scores")

     def __init__(
         self,
         replica_id: int,
         seed: int,
         scores: dict[str, float],
     ):
          self.replica_id = replica_id 
          self.seed = seed 
          self.scores = scores

class BootstrapTraceability:

     def __init__(self, n_replicas: int) -> None:
          self._n_replicas = n_replicas
          self._records: list[ReplicaRecord] = []
          self._best_by_key: dict[str, dict[str, int]] = {}



# File cabinet
def register(
        self,
        replica_id: int,
        seed: int,
        scores: dict[str, float],
) -> None:
     self._records.append(ReplicaRecord(replica_id, seed, scores))

# Select the winning replica
def set_best(self, key: str, group: str, replica_id: int) -> None:
     if key not in self._best_by_key:
          self._best_by_key[key] = {}
     self._best_by_key[key][group] = replica_id



def get_best_replica_id(self, key : str, group: str) -> int:
     return self._best_by_key[key][group]

def get_seed(self, replica_id:int) -> int:
    return self._records[replica_id].seed
    
def get_scores(self, replica_id: int) -> dict[str, float]:
     return self._records[replica_id].scores

def regenerate_indexes(
     self, 
     replica_id:int, 
     n_control:int, 
     n_treatment: int,
)    -> tuple[np.ndarray, np.ndarray]:
     
     seed = self.get_seed(replica_id)
     rng = np.random.default_rng(seed)

     bootstrap_c = pd.RangeIndex(n_control).to_series().sample(
           n=n_control, replace=True, random_state=rng
     )
     bootstrap_t = pd.RangeIndex(n_treatment).to_series().sample(
           n=n_treatment, replace=True, random_state=rng
     )
     return bootstrap_c.index.to_numpy(), bootstrap_t.index.to_numpy()

def get_best_sample(key:str, group:str, df_control:pd.DataFrame,
                    df_treatment:pd.DataFrame,) -> pd.DataFrame:
    replica_id = get_best_replica_id(key, group)
    n_c = len(df_control)
    n_t = len(df_treatment)
    idx_c, idx_t = regenerate_indexes(replica_id, n_c, n_t)
    return df_control.iloc[idx_c] if group == "control" else df_treatment.iloc[idx_t]


def to_dict(self) -> dict[str, Any]:
    return {
         "n_replicas": self._n_replicas,
         "records": [
              {
                   "replica_id": r.replica_id,
                   "seed": r.seed,
                   "scores": r.scores,
              }
              for r in self._records
         ],
         "best_by_key": self._best_by_key,
    }

def save(self, path: Path) -> None:
     path = Path(path)
     path.parent.mkdir(parents=True, exist_ok=True)
     with open(path, "w", encoding="utf-8") as f:
          json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

@classmethod
def load(cls, path: Path) -> "BootstrapTraceability":
     with open(path, encoding="utf-8") as f:
         data = json.load(f)
     inst = cls(n_replicas=data["n_replicas"])
     inst._records = [
         ReplicaRecord(r["replica_id"], r["seed_control"], r["seed_treatment"], r["scores"])
         for r in data["records"]
     ]
     inst._best_by_variable = data["best_by_variable"]
     return inst


# Summary for reporting
def to_summary_df(self) -> pd.DataFrame:
     """A readeable DatFrame showing the winners by variable and group."""
     rows: list[dict[str, Any]] = []
     for var, groups in self._best_by_variable.items():
         for group, rep_id in groups.items():
             seed_c, seed_t = self.get_seed_pair(rep_id)
             score = self.get_scores(rep_id).get(var, np.nan)
             rows.append({
                 "variable": var,
                 "group": group,
                 "best_replica_id": rep_id,
                 "seed_control": seed_c,
                 "seed_treatment": seed_t,
                 "coef_representatividad": score,
             })
     return pd.DataFrame(rows)

