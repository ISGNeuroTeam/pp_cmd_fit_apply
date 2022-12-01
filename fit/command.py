import pandas as pd

from joblib import dump
from pathlib import Path
from otlang.sdk.syntax import Keyword, Positional, OTLType
from pp_exec_env.base_command import BaseCommand, Syntax
from ts_forecasting.ts_forecasting import TimeSeriesForecaster
from ts_forecasting.model_params import ModelParams
from ts_forecasting.model_storage import Storage


class FitCommand(BaseCommand):
    # define syntax of your command here
    syntax = Syntax(
        [
            Positional("model_type", required=True, otl_type=OTLType.TERM),
            Positional("target_col", required=True, otl_type=OTLType.STRING),
            Positional("from_word", required=True, otl_type=OTLType.TERM),
            Positional("feature_cols", required=True, otl_type=OTLType.STRING),
            Positional("into_word", required=True, otl_type=OTLType.TERM),
            Positional("model_name", required=True, otl_type=OTLType.TEXT),
            Keyword("time_field", required=False, otl_type=OTLType.TEXT),
            Keyword("private", required=False, otl_type=OTLType.BOOLEAN)
        ],
    )
    use_timewindow = False  # Does not require time window arguments
    idempotent = True  # Does not invalidate cache

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        self.log_progress('Start ts_fit command')

        # Check model type
        model_type = self.get_arg('model_type').value
        if model_type not in ModelParams.MODELS:
            model_types_str = '\n'.join([f'- {key} - {value}' for key, value in ModelParams.MODELS.items()])
            raise ValueError(f'Unsupported forecaster type. Known types is:\n {model_types_str}')

        # Check from word
        from_word = self.get_arg("from_word").value
        if from_word != 'from':
            raise ValueError("Expecting 'from' key word")
        into_word = self.get_arg("into_word").value
        if into_word != 'into':
            print(into_word)
            raise ValueError("Expecting 'into' key word")

        feature_cols = list(map(
            lambda x: x.strip(),
            self.get_arg('feature_cols').value.split(',')
        ))

        target_col = self.get_arg('target_col').value

        model_name = self.get_arg('model_name').value

        time_field = self.get_arg('time_field').value or '_time'
        if time_field not in df.columns:
            raise ValueError(f'Time column "{time_field}" not exist')

        df['dt'] = pd.to_datetime(df[time_field], unit='s')
        df = df.set_index('dt')

        model_params = ModelParams(
            is_boxcox=False, is_autoregression=True, name=model_type
        )
        model = TimeSeriesForecaster.from_params(params=model_params)
        copy_df = df.copy()
        model.fit(
            target_df=copy_df[[target_col]],
            target_col=target_col,
            features_df=copy_df[feature_cols],
            features_cols=feature_cols
        )

        private = self.get_arg('private').value or False
        Storage(
            self.config['dir']['model_dir']
        ).save(model, model_name, self.platform_envs['user_guid'], private)

        predicted_df = model.predict(
            features_df=copy_df,
            features_cols=feature_cols,
            target_col_as=f'{model_name}_prediction'
        )

        df = pd.concat([df, predicted_df[[f'{model_name}_prediction']]], axis=1)
        df = df.reset_index().drop(columns=['dt'])

        return df
