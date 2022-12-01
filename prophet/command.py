import pandas as pd
from otlang.sdk.syntax import Keyword, Positional, OTLType
from pp_exec_env.base_command import BaseCommand, Syntax

from ts_forecasting.model_params import ModelParams
from ts_forecasting.ts_forecasting import TimeSeriesProphetForecaster


class ProphetCommand(BaseCommand):
    # define syntax of your command here
    syntax = Syntax(
        [
            Positional("target_name", required=True, otl_type=OTLType.TEXT),
            Keyword("future", required=False, otl_type=OTLType.INTEGER),
            Keyword("modelType", required=False, otl_type=OTLType.TEXT),
            Keyword("period", required=False, otl_type=OTLType.TEXT),
            Keyword("time_field", required=False, otl_type=OTLType.TEXT)
        ],
    )
    use_timewindow = False  # Does not require time window arguments
    idempotent = True  # Does not invalidate cache

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        column_name = self.get_arg('target_name').value

        if column_name not in df.columns:
            raise ValueError(f'Target {column_name} doesn\'t exist in dataframe')

        future_periods = self.get_arg('future').value

        model_type = self.get_arg('modelType').value or 'multiplicative'
        if model_type not in ModelParams.SEASONALITY_MODES:
            raise ValueError(f'Wrong model type. Available model types: additive, multiplicative')

        period = self.get_arg('period').value or 'D'
        period = period.upper()
        if period not in ('1H', '1D', 'H', 'D'):
            raise ValueError(f'Period must be one of: "H" or "D"')
        if period[0] == '1':
            period = period[1]

        time_field = self.get_arg('time_field').value or '_time'

        df['dt'] = pd.to_datetime(df[time_field], unit='s')
        df = df.set_index('dt')

        model_params = ModelParams(
            name='prophet', seasonality_mode=model_type,
            is_boxcox=False, is_autoregression=False,
            freq=period
        )
        model = TimeSeriesProphetForecaster(model_params)
        model.fit(df, column_name)
        result_df = model.predict(future_periods, target_col_as='prophet_prediction')

        result_df[time_field] = result_df.index.view('int64') // 1000000000
        result_df = result_df.reset_index().drop(columns=['dt'])

        return result_df[[time_field, 'prophet_prediction']]
