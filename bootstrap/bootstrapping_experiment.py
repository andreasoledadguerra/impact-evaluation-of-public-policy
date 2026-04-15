import pandas as pd
import numpy as np

from bootstrap.models import (
    BootstrapStats, 
    BootstrapStatsBinary, 
    BootstrapStatsCategorical, 
    BootstrapStatsContinuous, 
    StatsType,
)

from representativity.smd import SMDCalculator

class BootstrapExperiment:

    def __init__(
        self,
        data: tuple[pd.DataFrame, pd.DataFrame],
        columns: list[str],
        random_state: int = 42
    ) -> None:
        
        self._df_control, self._df_treatment = data
        self._columns = columns
        self._random_state = random_state

    # Automatization

        self.bootstrap_c, self.bootstrap_t = self._generate_samples()
        self.stats_c = self._calculate_stats(self.bootstrap_c)
        self.stats_t = self._calculate_stats(self.bootstrap_t)
        self.smd = self._calculate_smd()


    # Private methods

    def _generate_samples(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        bootstrap_c = self._df_control[self._columns].sample(
                 n = len(self._df_control),
            replace = True,
            random_state = self._random_state
        )
        bootstrap_t = self._df_treatment[self._columns].sample(
                 n = len(self._df_treatment),
            replace = True,
            random_state = self._random_state
        )
        return bootstrap_c, bootstrap_t


    # se usa para iterar por grupo, es decir que al invocar
    # debo implementarlo dos veces: uno para que haga cálculos sobre 
    # el grupo control y otro sobre el grupo tratamiento

    def _calculate_stats(
            self,
            bootstrap_samples: pd.DataFrame
    ) -> dict[str, StatsType]:
        """
        Calcula estadísticas resumen para cada columna según su tipo:
        - numérica continua (NUM_COLUMNS) -> media y desviación estándar (BootstrapStatsContinuous)
        - categórica condicional (CAT_CONDITIONS) -> proporciones por categoría (BootstrapStatsCategorical)
        - binario (SPC_COLUMNS) -> proporción 0-1 (BootstrapStatsBinary)
        """

        stats = {}
        
        for col in self._columns:
            serie = bootstrap_samples[col].dropna()
            n     = int(serie.count())

            # ---------Rama 1: numérica continua--------------------------
            if pd.api.types.is_numeric_dtype(serie) and col not in self._spc_columns:
                stats[col] = self._stats_for_continuous(serie, n)

            # ----------Rama 2: categórica condicional -------------------
            elif col in self._cat_conditions:
                stats[col]= self._stats_for_categorical(
                serie, col, self._cat_conditions[col]
            )

            # ----------Rama 3: binario -----------------------------------
            elif col in self._spc_columns:
                stats[col] = self._stats_for_binary(serie,n)


            # Si no entra en ninguna rama, registra una advertencia o ignorar
            else:
                logging.warning(f"Columna '{col}' de tipo no soportado, omitida.")

            return stats

        # -------------------Métodos auxiliares privados ---------------------
        @staticmethod
        def _stats_for_continuous(serie: pd.Series, n:int) -> BootstrapStatsContinuous:
            """ 
            Calcula estadísticas para variables numéricas continuas.

            """
            std = float(serie.std(ddof=1))
            return BootstrapStatsContinuous(
                mean=float(serie.mean()),
                std=std,
                var=float(serie.var(ddof=1)),
                dtype_kind="continua",
                n=n,
            )

        @staticmethod
        def _stats_for_categorical(serie:pd.Series, col_name:str, allowed_categories: List[str]
        ) -> BootstrapStatsCategorical:
            """ 
            Calcula proporciones para variables categóricas filtrando solo las categrorías permitidas definidas en _cat_conditions.
            """
            filtered = serie[serie.isin(allowed_categories)]
            n_filtered= int(filtered.count())

            if n_filtered == 0:
                raise ValueError(
                    f"Columna '{col_name}': ninguna observación pertenece a las categorías"
                    f"permitidas {allowed_categories}."
                )
            
            # Calcular proporciones normalizadas (suman 1)
            proportions = (filtered.value_counts(normalize=True)).to_dict()
            # Convertir claves a string 
            proportions = {str(k): float(v) for k, v in proportions.items()}

            return BootstrapStatsCategorical(
                n = n_filtered,
                proportions=proportions,
            )








    
    def calculate_smd(self, df, columns, grupo_col, df_treatment, df_control):
        """
        Calcula el SMD para un conjunto de columnas dado un grupo tratamiento/control.

        Parameters
        ----------
        df          : DataFrame completo
        columnas    : lista de columnas a evaluar
        grupo_col   : nombre de la columna que define los grupos
        grupo_trat  : valor del grupo tratamiento
        grupo_ctrl  : valor del grupo control
        """
        g1 = df[df[grupo_col] == df_treatment]
        g2 = df[df[grupo_col] == df_control]

        results = []

        for col in columns:
            x1 = g1[col].dropna()
            x2 = g2[col].dropna()
            dtype = df[col].dtype

            # --- Continua ---
            if pd.api.types.is_numeric_dtype(dtype) and not pd.api.types.is_bool_dtype(dtype):
                smd = smd_continuous(x1, x2)
                results.append({
                    "variable": col,
                    "tipo": "continua",
                    "categoria": "-",
                    "SMD": round(smd, 4),
                    "abs_SMD": round(abs(smd), 4)
                })

            # --- Booleana / binaria ---
            elif pd.api.types.is_bool_dtype(dtype):
                smd = smd_binary(x1.astype(float), x2.astype(float))
                results.append({
                    "variable": col,
                    "tipo": "binaria (bool)",
                    "categoria": "-",
                    "SMD": round(smd, 4),
                    "abs_SMD": round(abs(smd), 4)
                })

            # --- Categórica nominal (object) ---
            elif pd.api.types.is_object_dtype(dtype):
                smds_cat = smd_categorical(x1, x2)
                for cat, smd in smds_cat.items():
                    if not np.isnan(smd):
                        results.append({
                            "variable": col,
                            "tipo": "categórica (dummy)",
                            "categoria": cat,
                            "SMD": round(smd, 4),
                            "abs_SMD": round(abs(smd), 4)
                        })

        return pd.DataFrame(results).sort_values("abs_SMD", ascending=False)
