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