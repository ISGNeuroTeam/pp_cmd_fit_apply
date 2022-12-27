import pandas as pd
from otlang.sdk.syntax import Keyword, Positional, OTLType
from pp_exec_env.base_command import BaseCommand, Syntax
from ts_forecasting import distr


class GenDistrCommand(BaseCommand):
    # define syntax of your command here
    syntax = Syntax(
        [
            Positional("distr_name", required=True, otl_type=OTLType.STRING),
            Keyword("size", required=False, otl_type=OTLType.INTEGER),
            Keyword("to_file", required=False, otl_type=OTLType.TEXT),

            # PERT params:
            Keyword("a", required=False, otl_type=OTLType.NUMBERIC),
            Keyword("b", required=False, otl_type=OTLType.NUMBERIC),
            Keyword("c", required=False, otl_type=OTLType.NUMBERIC),
        ],
    )
    use_timewindow = False  # Does not require time window arguments
    idempotent = True  # Does not invalidate cache

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        self.log_progress('Start gen_distr command')

        # Check distribution name
        distr_name = self.get_arg('distr_name').value
        if distr_name not in distr.DISTRIBUTIONS:
            raise ValueError(f'Unsupported distribution. Known distribution are: {", ".join(distr.DISTRIBUTIONS.keys())}')

        # Check size
        size = self.get_arg('size').value or 1

        # Output file
        to_file = self.get_arg('to_file').value

        # Check params
        params = dict()
        if distr_name == 'pert':
            for param_name in ['a', 'b', 'c']:
                if (param_val := self.get_arg(param_name).value) is None:
                    raise ValueError(f'Missing param for PERT distribution: {param_name}')
                params[param_name] = param_val

        result_df = distr.generate(name=distr_name, size=size, **params)

        if to_file:
            result_df.to_parquet(to_file)

        return result_df
