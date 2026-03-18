import numpy as np
from pydantic import BaseModel, Field

class BoostrapStats(BaseModel):
    mean: float
    var: float


