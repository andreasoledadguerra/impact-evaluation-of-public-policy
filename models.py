import numpy as np
from pydantic import BaseModel, Field, model_validator
from src.utils import _calculate_media_std, calculate_media_condition
from constants import NUM_COLUMNS, CAT_CONDITIONS, SPC_COLUMNS

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


PopulationStatType = Stats | Proportions

class GruopSummary:

  def __init__(self, df):
    self.df = df
    self.summary = self._calculate()

  def _calculate(self) -> dict[str, PopulationStatType]:
    result = {}

    for col in NUM_COLUMNS + SPC_COLUMNS:
      serie = self.df[col].dropna()
      mean, std = _calculate_media_std(self.df, col)
      result[col] = Stats(
        column = col,
        mean = mean,
        std = std,
        n = int(serie.count())
      )

    for col, categories in CAT_CONDITIONS.items():
      serie = self.df[col].dropna()
      filtered = serie[serie.isin(categories)]
      props = (
        filtered
        .value_counts(normalize=True)
        .round(4)
        .to_dict()
      )
      result[col] = Proportions(
        column = col,
        proportions = {str(k): float(v) for k, v in props.items()},
              n = int(serie.count())
      )

    return result

  