import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd




#def register(
#        #self,
#        replica_id: int,
#        seed_control: int,
#        seed_treatment: int,
#        scores: dict[str, float],
#) -> None:


def get_best_replica_id(
          key : str, group: str) -> int:
     return dict[key][group]

def get_seed(
          replica_id:int) -> tuple[int, int]:
    rec = records[replica_id]
    return rec.seed_control, rec.seed_treatment

def get_scores(replica_id: int) -> dict[str, float]:
     return records[replica_id].scores

def regenerate_indexes(replica_id:int, n_control:int, n_treatment: int,) -> tuple[np.ndarray, np.ndarray]:
     seed = get_seed(replica_id)
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
