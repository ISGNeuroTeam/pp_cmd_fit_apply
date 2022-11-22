import os
import pickle

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from datetime import datetime
import numpy as np
import pandas as pd
from prophet import Prophet
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Lasso
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor, DMatrix

from .ts_feature_extraction import extract_autoregression_features, add_autoregression_features
from .model_params import ModelParams
from .constants import *


class TimeSeriesForecaster(ABC):
    params: ModelParams
    pipeline: Pipeline
    features_: List[str] = None
    autoregression_features_: Optional[Dict] = None
    selected_features_: Optional[List[str]] = None

    def __init__(self, params: ModelParams):
        self.params = params

        self.pipeline = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='mean')),
            # TODO: средними - плохо, лучше заполнять соседними значениями (предыдущими или следующими) или средними за тот же день недели/месяца/года
            ('scaler', StandardScaler()),
            ('regressor', self.create_regressor()),
        ])

    @abstractmethod
    def get_regressor_params(self) -> Dict:
        pass

    @abstractmethod
    def get_regressor_class(self):
        pass

    def create_regressor(self) -> None:
        return self.get_regressor_class()(**self.get_regressor_params())

    def fit(self,
            target_df: pd.DataFrame,
            target_col: str,
            features_df: Optional[pd.DataFrame] = None,
            features_cols: Optional[List[str]] = None) -> 'TimeSeriesForecaster':
        target_df = target_df.copy()
        if self.params.is_boxcox:
            target_df[target_col] = np.log(target_df[target_col] + 0.0001)
        # Формируем датафреймы для обучения
        # У фичей и таргета должны полностью совпадать индексы (DateTimeIndex)
        if features_df is not None:
            train_df = pd.concat([target_df, features_df], axis=1)
            train_df = train_df[~train_df[target_col].isnull()].dropna(how='all', subset=features_cols)

            # 19-10-2022:
            self.trend_model_ = None
        else:
            if not self.params.is_autoregression:
                #raise ValueError("Either autoregression flag or features dataframe must be set!")
                self.params.is_autoregression = True
            #train_df = target_df

            # 19-10-2022: detrend:
            X_trend = np.arange(0, len(target_df)).reshape(-1, 1)
            self.X_trend_history_ = X_trend
            self.trend_model_ = LinearRegression().fit(X_trend, target_df[target_col])
            global_trend = self.trend_model_.predict(X_trend)
            target_df[target_col] = target_df[target_col] / global_trend

            train_df = target_df

        if self.params.name == 'prophet':
            self.params.is_autoregression = False  # у Prophet своя авторегрессия внутри

        if self.params.is_autoregression:
            # Добавляем свои фичи
            self.autoregression_features_ = extract_autoregression_features(train_df, target_col, freq='H')  # TODO: freq=
            train_df, new_features = add_autoregression_features(train_df, self.autoregression_features_)
            if features_df is not None:
                features_cols = list(features_cols) + new_features #if features_df is not None else new_features
            else:
                features_cols = new_features

        self.features_ = features_cols

        y_train = train_df[target_col]
        X_train = train_df[features_cols]

        self.pipeline.fit(X_train, y_train)

        return self

    def predict(self,
                features_df: Optional[pd.DataFrame] = None,
                features_cols: Optional[List[str]] = None,
                for_date: Optional[Any] = None,
                start_date: Optional[Any] = None,
                target_col_as: Optional[str] = None) -> pd.DataFrame:
        if features_df is None:
            if not for_date:
                raise ValueError("Need either features_df or for_date param to be set!")
            if not start_date:
                raise ValueError("Need either features_df of start_date param to be set!")
            freq = self.params.freq
            dates = pd.date_range(start=start_date, end=for_date, freq=freq)
            features_df = pd.DataFrame(index=dates)
            features_df.index.name = "dt"
        if self.params.is_autoregression and self.autoregression_features_:
            features_df, new_features = add_autoregression_features(features_df, self.autoregression_features_)
            if features_cols:
                features_cols = list(features_cols) + new_features
            else:
                features_cols = new_features
        X = features_df[features_cols]
        pred = self.pipeline.predict(X)
        # 19-10-2022:
        if self.trend_model_ is not None:
            X_trend = np.arange(len(self.X_trend_history_), len(self.X_trend_history_) + len(pred)).reshape(-1, 1)
            global_trend = self.trend_model_.predict(X_trend)
            pred = pred * global_trend
        if self.params.is_boxcox:
            pred = np.exp(pred)
        target_col = target_col_as if target_col_as else 'value_pred'
        return pd.DataFrame(pred, index=X.index, columns=[target_col])

    def persist(self, folder: str):
        persist_path = os.path.join(folder, f"{self.params.name}.pickle")
        with open(persist_path, "wb") as f:
            pickle.dump(self.pipeline, f)

    @classmethod
    def from_params(cls, params: ModelParams) -> 'TimeSeriesForecaster':
        if params.name == 'xgb':
            return TimeSeriesXGBForecaster(params)
        elif params.name == 'rf':
            return TimeSeriesRandomForestForecaster(params)
        elif params.name == 'lr':
            return TimeSeriesLinearRegressionForecaster(params)
        else:
            raise ValueError(f"Unknown time series forecasting model: {params.name}")


class TimeSeriesLinearRegressionForecaster(TimeSeriesForecaster):
    def get_regressor_params(self) -> Dict:
        return {
            #"alpha": 0.1  # TODO: cv search best alpha
        }

    def get_regressor_class(self):
        return LinearRegression  #Lasso

    def get_coeffs(self) -> List:
        return list(zip(self.features_, self.pipeline.named_steps["regressor"].coef_))


class TimeSeriesRandomForestForecaster(TimeSeriesForecaster):
    def get_regressor_params(self) -> Dict:
        return {
            #"max_depth": 100,
            "max_features": "auto",
            "n_estimators": 20,
            "criterion": "absolute_error",
        }

    def get_regressor_class(self):
        return RandomForestRegressor


class TimeSeriesXGBForecaster(TimeSeriesForecaster):
    def get_regressor_params(self) -> Dict:
        return {
            "learning_rate": 0.1,
            "max_depth": 100,
            "n_estimators": 100,
        }

    def get_regressor_class(self):
        return XGBRegressor
