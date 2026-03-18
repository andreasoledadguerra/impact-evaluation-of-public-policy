import numpy as np
from pydantic import BaseModel, Field

class BootsrapStats(BaseModel):
    mean: float = Field (..., description="Media de la muestra bootstrap")
    var: float = Field ( ..., ge=0, description="Varianza (ddof=1)")

    class Config:
        frozen = True
