import pandas as pd
from otlang.sdk.syntax import Keyword, Positional, OTLType
from pp_exec_env.base_command import BaseCommand, Syntax

from ts_forecasting.ts_forecasting import TimeSeriesLinearRegressionForecaster
from ts_forecasting.model_storage import Storage

class GetCoeffsCommand(BaseCommand):
    # define syntax of your command here
    syntax = Syntax(
        [
            Positional("model_name", required=True, otl_type=OTLType.TEXT),
            Keyword("private", required=False, otl_type=OTLType.BOOLEAN)
        ],
    )
    use_timewindow = False  # Does not require time window arguments
    idempotent = True  # Does not invalidate cache

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        model_name = self.get_arg('model_name').value
        model: TimeSeriesLinearRegressionForecaster = Storage(self.config['dir']['model_dir']).load(
            model_name, self.platform_envs['user_guid'], private=self.get_arg('private').value
        )
        data = model.get_coeffs()
        return pd.DataFrame(data, columns=['feature', 'coeff'])
