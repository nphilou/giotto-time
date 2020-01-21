from typing import Callable

import pandas as pd
from scipy.optimize import minimize
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.metrics import mean_squared_error
from sklearn.utils.validation import check_is_fitted

from giottotime.utils.trends import TRENDS


class TrendForecaster(BaseEstimator, RegressorMixin):
    def __init__(self, trend, trend_init, loss: Callable = mean_squared_error, method: str = "BFGS"):
        self.trend = trend
        self.trend_init = trend_init
        self.loss = loss
        self.method = method

    def fit(self, X, y=None):
        """Fit the estimator.

        Parameters
        ----------
        X : pd.DataFrame, shape (n_samples, n_features)
            Input data.

        y : None
            There is no need of a target in a transformer, yet the pipeline API
            requires this parameter.

        Returns
        -------
        self : object
            Returns self.
        """

        if self.trend not in TRENDS:
            raise ValueError("The trend '%s' is not supported. Supported "
                             "trends are %s."
                             % (self.trend, list(sorted(TRENDS))))

        self.best_trend_params_ = minimize(
            lambda opt: self.loss(X.values, [TRENDS[self.trend](t, opt) for t in range(0, X.shape[0])]),
            self.trend_init,
            method=self.method,
            options={"disp": False},
        )["x"]

        return self

    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        """Using the fitted polynomial, predict the values starting from ``X``.

        Parameters
        ----------
        ts: pd.DataFrame, shape (n_samples, 1), required
            The time series on which to predict.

        Returns
        -------
        predictions : pd.DataFrame, shape (n_samples, 1)
            The output predictions.

        Raises
        ------
        NotFittedError
            Raised if the model is not fitted yet.

        """
        check_is_fitted(self)

        predictions = TRENDS[self.trend](X.values, self.best_trend_params_)
        return predictions