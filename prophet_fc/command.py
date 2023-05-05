import pandas as pd
from otlang.sdk.syntax import Keyword, OTLType
from pp_exec_env.base_command import BaseCommand, Syntax

from prophet_fc.prophet_lib import get_prophet_forecast


class ProphetCommand(BaseCommand):
    # define syntax of your command here
    syntax = Syntax(
        [
            Keyword("target_col", required=True, otl_type=OTLType.TEXT),
            Keyword("periods", required=True, otl_type=OTLType.INTEGER),
            Keyword("freq", required=False, otl_type=OTLType.TEXT),
            Keyword("time_col", required=False, otl_type=OTLType.TEXT),
            Keyword("time_epoch", required=False, otl_type=OTLType.BOOLEAN)
        ],
    )
    use_timewindow = False  # Does not require time window arguments
    idempotent = True  # Does not invalidate cache

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        target_column = self.get_arg('target_col').value
        if target_column not in df.columns:
            raise ValueError(f'Target {target_column} doesn\'t exist in dataframe')

        periods = self.get_arg('periods').value
        time_column = self.get_arg('time_col').value or '_time'
        time_epoch = self.get_arg('time_epoch').value or False
        unit = 's' if time_epoch else None

        df[time_column] = pd.to_datetime(df[time_column], unit=unit)
        if not df[time_column].is_monotonic_increasing:
            df.sort_values(by=time_column, inplace=True)
        freq = self.get_arg('freq').value or pd.infer_freq(df[time_column])
        df.rename(columns={time_column: 'ds'}, inplace=True)
        df.rename(columns={target_column: 'y'}, inplace=True)

        result = get_prophet_forecast(df, periods, freq)
        # result_df['_time'] = result_df.index.view('int64') // 1000000000

        # return result_df[['_time', 'value_pred']]
        return result
