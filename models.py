import numpy as np
from pydantic import BaseModel, Field, model_validator

class Stats(BaseModel, frozen=True):
  column: str
  mean: float
  std: float
  n: int = Field(..., gt=0)

class Proportions(BaseModel, frozen=True):
  column: str
  proportions: dict[str, float]
  n: int = Field(..., gt=0)

  @model_validator(mode='after')
  def validate_proportions(self) -> 'Proportions':
    total_proportion = sum(self.proportions.values())
    if not np.isclose(total_proportion, 1.0, atol=1e-5):
      raise ValueError(f"Total proportion must be 1.0, got {total_proportion}")
    return self