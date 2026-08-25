from pydantic import BaseModel, Field, model_validator
from src.utils import _calculate_media_std
from constants import NUM_COLUMNS, CAT_CONDITIONS, SPC_COLUMNS