import numpy as np
from pydantic import BaseModel, Field, computed_field, model_validator

class BootstrapStats(BaseModel):
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
    
    class Config:
        frozen = True 
