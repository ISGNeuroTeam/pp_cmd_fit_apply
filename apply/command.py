import pandas as pd
from pathlib import Path
from joblib import load

from otlang.sdk.syntax import Keyword, Positional, OTLType
from pp_exec_env.base_command import BaseCommand, Syntax

from ts_forecasting.ts_forecasting import TimeSeriesLinearRegressionForecaster


class ApplyCommand(BaseCommand):
    # define syntax of your command here
    syntax = Syntax(
        [
            Positional("model_name", required=True, otl_type=OTLType.TEXT),
            Keyword("time_field", required=False, otl_type=OTLType.TEXT)
        ],
    )
    use_timewindow = False  # Does not require time window arguments
    idempotent = True  # Does not invalidate cache

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        model_name = self.get_arg('model_name').value
        models_dir = Path(self.config['dir']['model_dir'])
        if not models_dir.exists():
            raise ValueError(f'Models directory "{models_dir}" not exist')
        full_model_path = Path(self.config['dir']['model_dir']) / model_name

        time_field = self.get_arg('time_field').value or '_time'
        df['dt'] = pd.to_datetime(df[time_field], unit='s')
        df = df.set_index('dt')

        model: TimeSeriesLinearRegressionForecaster = load(full_model_path)
        predicted_df = model.predict(
            features_df=df,
            features_cols=model.non_ar_features_,
            target_col_as=f'{model_name}_prediction'
        )
        predicted_df[time_field] = predicted_df.index.view('int64') // 1000000000
        predicted_df = predicted_df.reset_index().drop(columns=['dt'])

        return predicted_df
