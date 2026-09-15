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
          variable: str, group: str) -> int:
     return dict[variable][group]

def get_seed_pair(
          replica_id:int) -> tuple[int, int]:
    rec = records[replica_id]
    return rec.seed_control, rec.seed_treatment

def get_scores(replica_id: int) -> dict[str, float]:
     return records[replica_id].scores

def regenerate_indexes(replica_id:int, n_control:int, n_treatment: int,) -> tuple[np.ndarray, np.ndarray]:
    seed_c, seed_t = get_seed_pair(replica_id)
    rng_c = np.random.default_rng(seed_c)
    rng_t = np.random.default_rng(seed_t)
    idx_c = rng_c.integers(0, n_control, size=n_control)
    idx_t = rng_t.integers(0, n_treatment, size=n_treatment)
    return idx_c, idx_t