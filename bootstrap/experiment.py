import pandas as pd

from bootstrap.models import BoostrapStats

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
    
    def _calculate_stats(
            self,
            bootrap_samples: pd.DataFrame
    ) -> dict[str, BootstrapStats]:
        return {
            col: BootstrapStats(
                mean = float(bootstrap_samples[col].mean()),
                var = float(bootrap_samples[col].var(ddof=1))
            )
            for col in self._columns
        }