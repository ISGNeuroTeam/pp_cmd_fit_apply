import pandas as pd
from prophet import Prophet


def get_prophet_forecast(df: pd.DataFrame, periods: int, freq: str):
    m = Prophet()
    m.fit(df=df)
    future = m.make_future_dataframe(periods=periods, include_history=False, freq=freq)
    forecast = m.predict(future)

    forecast['ds'] = forecast['ds'].view('int64') // 1000000000
    forecast.rename(columns={'yhat': 'prophet_predictions'}, inplace=True)
    forecast.rename(columns={'ds': '_time'}, inplace=True)

    return forecast[['_time', 'prophet_predictions']]
