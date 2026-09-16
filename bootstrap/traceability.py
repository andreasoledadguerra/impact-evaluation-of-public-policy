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
     seed = get_seed

def get_best_sample(variable:str, group:str, df_control:pd.DataFrame,
                    df_treatment:pd.DataFrame,) -> pd.DataFrame:
    replica_id