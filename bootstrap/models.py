import numpy as np
from pydantic import BaseModel, 

class BoostrapStats(BaseModel):
    mean: float
    var: float


