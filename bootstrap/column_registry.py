from typing import Literal

ColumnKind =Literal["continua", "binaria", "categorica"]

class ColumnRegistry:
    """
    Registry for column types in the dataset.
    """

    def __init__(
        self,
        num_columns: list[str],
        cat_conditions: dict[str, list[str]],
        spc_columns:list[str],
    ) -> None:
        self._kind_by_column: dict[str, ColumnKind] = {}
        self._cat_conditions = cat_conditions

        for col in num_columns:
            self._register(col, "continua")
        for col in cat_conditions:
            self._register(col, "categorica")
        for col in spc_columns:
            self._register(col, "binaria")