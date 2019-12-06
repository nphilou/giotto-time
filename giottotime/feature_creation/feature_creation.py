from typing import List

import numpy as np
import pandas as pd

from .base import TimeSeriesFeature
from .time_series_features import ShiftFeature

__all__ = ["FeatureCreation"]


def check_feature_names(time_series_features: List[TimeSeriesFeature]) -> None:
    """Check that all the output names are different and that there aren't two different
    features with the same name.

    Parameters
    ----------
    time_series_features : ``List[TimeSeriesFeature]``, required.
        The list of features.

    Returns
    -------
    None

    Raises
    ------
    ``ValueError``
        Raised if there are two features with the same name.

    """
    feature_output_names = [feature.output_name for feature in time_series_features]
    if len(set(feature_output_names)) != len(feature_output_names):
        raise ValueError(
            "The input features should all have different names, instead "
            f"they are {feature_output_names}."
        )


class FeatureCreation:
    """Class responsible for the generation of the feature_creation, starting
    from a list of ``TimeSeriesFeature``.

    Parameters
    ----------
    horizon : ``int``, required.
        It represents how much into the future is necessary to predict. This
        corresponds to the number of shifts that are going to be performed
        on y.

    time_series_features : ``List[TimeSeriesFeature]``, required.
        The list of ``TimeSeriesFeature`` from which to compute the
        feature_creation.

    """

    def __init__(self, horizon: int, time_series_features: List[TimeSeriesFeature]):
        check_feature_names(time_series_features)

        self._time_series_features = time_series_features
        self._horizon = horizon

    def fit_transform(self, time_series: pd.DataFrame) -> (pd.DataFrame, pd.DataFrame):
        """Create the X matrix by generating the feature_creation, starting
        from the original ``time_series`` and using the list of
        ``time_series_features``. Also create the y matrix, by generating
        ``horizon`` number of shifts of the ``time_series``.

        Parameters
        ----------
        time_series : ``pd.DataFrame``, required.
            The time-series on which to compute the ``X`` and ``y`` matrices.

        Returns
        -------
        x, y: ``(pd.DataFrame, pd.DataFrame)``
            A tuple containing the ``X`` and ``y`` matrices.

        """
        x = self._create_x_features(time_series)
        y = self._create_y_shifts(time_series)
        return x, y

    def _create_y_shifts(self, time_series: pd.DataFrame) -> pd.DataFrame:
        """Generate ``n`` shifts of ``time_series``, where ``n`` is equal to
        the ``horizon``.

        Parameters
        ----------
        time_series : ``pd.DataFrame``, required.
            The original DataFrame on which to generate the shifts.

        Returns
        -------
        y_shifted : ``pd.DataFrame``
            The DataFrame containing the shifts of ``time_series``.

        """
        y = pd.DataFrame(index=time_series.index)
        for k in range(self._horizon):
            shift_feature = ShiftFeature(-k, f"shift_{k}")
            y[f"y_{k}"] = shift_feature.fit_transform(time_series)

        return y

    def _create_x_features(self, time_series: pd.DataFrame) -> pd.DataFrame:
        """Create a DataFrame, containing a set of feature_creation generated
        from the ``time_series`` and using the ``time_series_features``.

        Parameters
        ----------
        time_series : ``pd.DataFrame``, required.
            The original DataFrame on which to generate the shifts.

        Returns
        -------
        feature_creation : ``pd.DataFrame``
            The DataFrame containing the feature_creation.

        """
        features = pd.DataFrame(index=time_series.index)
        for time_series_feature in self._time_series_features:
            x_transformed = time_series_feature.fit_transform(time_series)
            features = pd.concat([features, x_transformed], axis=1)

        return features
