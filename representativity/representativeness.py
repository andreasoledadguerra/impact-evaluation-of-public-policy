import numpy as np
import pandas as pd
from constants import NUM_COLUMNS, CAT_CONDITIONS, SPC_COLUMNS
from schema import Mean, Proportions


class RepresentativenessCalculator:

  @staticmethod
  def _numeric_mean(series: pd.Series) -> float:
      return float(series.mean())

  @staticmethod
  def _categorical_mean(series: pd.Series, condition) -> float:
      if callable(condition):
          mask = series.apply(condition)
      elif isinstance(condition, (list, tuple, set)):
          mask = series.isin(condition)
      else:
          mask = series == condition

      return float(mask.mean())

  @classmethod
  def _get_mean(
      cls,
      df:pd.DataFrame,
      column: str,
      var_config: dict,
  ) -> float:
      vtype = var_config.get("type", "numeric")

      if vtype == "numeric":
          return cls._numeric_mean(df[column])

      if vtype == "categorical":
            condition = var_config["condition"]
            return cls._categorical_mean(df[column], condition)

      if vtype == "special":
            return cls._numeric_mean(df[column])

      raise ValueError(f"Unknown variable type: {vtype}") 

  @staticmethod
  def abs_error_vs_population(sample_mean:float, population_mean: float) -> float:
      if np.isnan(sample_mean) or np.isnan(population_mean):
          return np.nan
      return float(abs(sample_mean - population_mean))


  @classmethod
  def rel_error_vs_population(cls, sample_mean: float, population_mean:float) -> float:
      abs_error = cls.abs_error_vs_population(sample_mean, population_mean)
      if population_mean == 0 or np.isnan(population_mean) or np.isnan(abs_error):
          return np.nan
      return float(abs_error / population_mean)

  @classmethod
  def perc_error_vs_population(cls, sample_mean: float, population_mean: float) ->float:
      relative_error = cls.rel_error_vs_population(sample_mean, population_mean)
      if np.isnan(relative_error):
          return np.nan
      return float(relative_error * 100)

  @classmethod
  def representativeness_coefficient(cls, sample_mean: float, population_mean: float) ->float:
    """
        Representativeness coefficient = 1 - relative_error
        Close to 1.0 -> high representativeness (low relative error).
        Since relative_error is always >= 0 (it is derived from the absolute error),
        this coefficient never exceeds 1.0, but it CAN be negative if the relative error exceeds 
        100% of the population mean (the sample deviates more than the value of the reference mean itself)

    """
    relative_error = cls.el_error_vs_population(sample_mean, population_mean)
    return np.nan if np.isnan(relative_error) else float(1 - relative_error)

#TODO refactorizar dde Kimi
  #classmethod
  def _mean_in_columns(
      processed_df: pd.DataFrame,
      data: tuple[pd.DataFrame, pd.DataFrame],
      column: str,
  ) -> dict:
      df_control, df_treatment = data

      mean_population = processed_df[column].mean()

      mean_c = df_control[column].mean()
      mean_t = df_treatment[column].mean()

      return {
        "column": column,
        "mean_population": mean_population,
        "mean_control": mean_c,
        "mean_treatment": mean_t,

    }
