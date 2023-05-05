import pandas as pd
from otlang.sdk.syntax import Keyword, Positional, OTLType
from pp_exec_env.base_command import BaseCommand, Syntax
from joblib import load
from pathlib import Path

from ts_forecasting.ts_forecasting import TimeSeriesLinearRegressionForecaster


class GetCoefCommand(BaseCommand):
    # define syntax of your command here
    syntax = Syntax(
        [
            Positional("model_name", required=True, otl_type=OTLType.TEXT),
        ],
    )
    use_timewindow = False  # Does not require time window arguments
    idempotent = True  # Does not invalidate cache

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        model_name = self.get_arg('model_name').value

        models_dir = Path(self.config['dir']['model_dir'])
        if not models_dir.exists():
            models_dir.mkdir(exist_ok=True)

        full_model_path = Path(self.config['dir']['model_dir']) / model_name

        model: TimeSeriesLinearRegressionForecaster = load(full_model_path)
        data = model.get_coeffs()
        return pd.DataFrame(data, columns=['feature', 'coef'])


