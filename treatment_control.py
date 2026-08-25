from models import Stats, Proportions
from pydantic import BaseModel, Field, model_validator
from src.utils import _calculate_media_std
from constants import NUM_COLUMNS, CAT_CONDITIONS, SPC_COLUMNS
# recibo     df_control, df_treatment = randomization(processed_df.df


class TreatmentControlSummary:

    def __init__(self, tuple):
        self.tuple = tuple
        self.summary = self._calculate()

    def _calculate(self) -> tuple[None, TreatmentControlType]:
