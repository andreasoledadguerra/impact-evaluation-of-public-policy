import numpy as np
from pydantic import BaseModel, Field, model_validator
from models import Stats, Proportions
from src.utils import _calculate_media_std, calculate_media_condition
from constants import NUM_COLUMNS, CAT_CONDITIONS, SPC_COLUMNS


PopulationStatType = Stats | Proportions

class PopulationSummary:

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