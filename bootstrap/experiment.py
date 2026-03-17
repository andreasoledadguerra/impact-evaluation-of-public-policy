import pandas as pd

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

    # Automatización

        self.bootstrap_c, self.bootstrap_t = self._generate_samples()
        self.stats_c = self._calculate_stats(self.bootstrap_c)
        self.stats_t = self._calculate_stats(self.bootstrap_t)
        self.smd = self._calculate_smd()

        
