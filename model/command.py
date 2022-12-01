import pandas as pd
from otlang.sdk.syntax import Keyword, Positional, OTLType
from pp_exec_env.base_command import BaseCommand, Syntax

from ts_forecasting.model_storage import Storage


class ModelCommand(BaseCommand):
    # define syntax of your command here
    syntax = Syntax(
        [
            Positional("command", required=True, otl_type=OTLType.TEXT),
            Positional("model_name", required=False, otl_type=OTLType.TEXT),
            Keyword("private", required=False, otl_type=OTLType.BOOLEAN)
        ],
    )
    use_timewindow = False  # Does not require time window arguments
    idempotent = True  # Does not invalidate cache

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        command = self.get_arg('command').value
        if command not in ('list', 'delete'):
            raise ValueError('Two command supported: list,  delete')

        model_storage = Storage(
            self.config['dir']['model_dir']
        )
        user_id = self.platform_envs['user_guid']

        if command == 'delete':
            model_storage.delete(
                self.get_arg('model_name').value, user_id, self.get_arg('private').value
            )

        return pd.DataFrame(
            model_storage.list(user_id), columns=['model_path', 'storage_type']
        )
