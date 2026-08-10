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

    def _register(self, col: str, kind: ColumnKind) -> None:
        if col in self._kind_by_column:
            raise ValueError(
                f"La columna '{col}' está declarada en más de un grupo de "
                f"tipo ({self._kind_by_column[col]!r} y {kind!r}). Cada "
                f"columna debe pertenecer a exactamente un tipo "
                f"(NUM_COLUMNS / CAT_CONDITIONS / SPC_COLUMNS)."
            )
        self._kind_by_column[col] = kind
 
    def kind_of(self, col: str) -> ColumnKind:
        """Tipo de una columna. Lanza KeyError si no está registrada."""
        try:
            return self._kind_by_column[col]
        except KeyError:
            raise KeyError(
                f"La columna '{col}' no está registrada en NUM_COLUMNS, "
                f"CAT_CONDITIONS ni SPC_COLUMNS."
            ) from None
 
    def allowed_categories(self, col: str) -> list[str]:
        """Categorías permitidas para una columna categórica (CAT_CONDITIONS)."""
        return self._cat_conditions[col]
 
