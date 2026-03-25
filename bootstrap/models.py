import numpy as np
from typing import Literal, Annotated
from pydantic import BaseModel, Field, computed_field, model_validator

class BootstrapStats(BaseModel, frozen=True):
    mean: float = Field (..., description="Media de la muestra bootstrap")
    std:  float = Field(..., ge=0, description="Desviación estándar (ddof=1)")
    var: float = Field ( ..., ge=0, description="Varianza (ddof=1)") # sample variance

    @computed_field
    @property
    def cv(self) -> float:
        """Coefficient of variation — useful to compare group's dispersion"""
        return self.std / self.mean if self.mean != 0 else 0.0

    # Validación cruzada entre campos
    @model_validator(mode='after')
    def validate_var_std_consistency(self) -> 'BootstrapStats':
        if not np.isclose(self.var, self.std ** 2, rtol=1e-5):
            raise ValueError(
                f"var ({self.var:.6f}) must be equal to std² ({self.std**2:.6f})"
            )
        return self
    

# --- Subclase para variables binarias (bool) ---
class BootstrapStatsBinary(BootstrapStats, frozen=True):
    """
    Para variables booleanas. mean = proporción p.
    Hereda validación de var = std² de la clase base.
    """
    dtype_kind: Literal["binaria"] = "binaria"
    n: int = Field(..., gt=0)
    mean: float = Field(..., ge=0,le=1, # restringe a [0,1]
                            description="Proporción p de la Bernoulli")

    @model_validator(mode='after')
    def validate_bernoulli_variance(self) -> 'BootstrapStatsBinary':
        """
        Para una Bernoulli: var teórica = p * (1 - p).
        Se ejecuta DESPUÉS del validador heredado de BootstrapStats.
        """
        expected_var = self.mean * (1 - self.mean)
        if not np.isclose(self.var, expected_var, rtol=1e-5):
            raise ValueError(
                f"Bernoulli variance mismatch: "
                f"var ({self.var:.6f}) != mean*(1-mean) ({expected_var:.6f})"
            )
        return self


# --- Subclase para variables continuas ---
class BootstrapStatsContinuous(BootstrapStats, frozen=True):
    """Para variables numéricas continuas."""
    dtype_kind: Literal["continua"] = "continua"
    n: int = Field(..., gt=0)


# --- Clase independiente para categóricas (no hereda — no tiene mean/std/var) ---
class BootstrapStatsCategorical(BaseModel, frozen=True):
    """
    Para variables nominales (object).
    No tiene mean/std/var — almacena proporciones por categoría.
    """
    dtype_kind: Literal["categorica"] = "categorica"
    n: int = Field(..., gt=0)
    proportions: dict[str, float] = Field(
        ..., description="Proporción de cada categoría en el grupo"
    )

    @model_validator(mode='after')
    def validate_proportions(self) -> 'BootstrapStatsCategorical':
        total = sum(self.proportions.values())
        if not np.isclose(total, 1.0, atol=1e-5):
            raise ValueError(f"Las proporciones deben sumar 1.0, suman {total:.6f}")
        return self


# Tipo unión para anotaciones
StatsType = Annotated[BootstrapStatsContinuous | BootstrapStatsBinary | BootstrapStatsCategorical, Field(discriminator="dtype_kind")]