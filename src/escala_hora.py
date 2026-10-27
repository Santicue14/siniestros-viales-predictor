"""Escala la hora sin asignar una hora de reloj a los faltantes."""

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin


class EscalaHoraSinImputar(BaseEstimator, TransformerMixin):
    """Escala la hora con la media y el desvío de las horas observadas.

    Las filas sin hora no entran en esa cuenta. Salen con la hora escalada
    en 0 y ``hora_faltante`` en 1. Ese 0 no es una hora del día: una hora
    real cercana a la media queda cerca de 0 con ``hora_faltante`` en 0.
    """

    def fit(self, X, y=None):
        hora = self._como_serie(X).to_numpy(dtype=float)
        observados = hora[~np.isnan(hora)]
        if observados.size == 0:
            raise ValueError("No hay horas observadas para escalar.")
        self.mean_ = float(observados.mean())
        self.scale_ = float(observados.std())
        if self.scale_ == 0:
            self.scale_ = 1.0
        self.n_features_in_ = 1
        return self

    def transform(self, X):
        hora = self._como_serie(X).to_numpy(dtype=float)
        faltante = np.isnan(hora).astype(float)
        escalada = (hora - self.mean_) / self.scale_
        escalada = np.where(np.isnan(hora), 0.0, escalada)
        return np.column_stack([escalada, faltante])

    def get_feature_names_out(self, input_features=None):
        return np.asarray(["rango_horario_escalado", "hora_faltante"], dtype=object)

    @staticmethod
    def _como_serie(X):
        import pandas as pd

        if isinstance(X, pd.DataFrame):
            return pd.to_numeric(X.iloc[:, 0], errors="coerce")
        return pd.to_numeric(pd.Series(np.asarray(X).ravel()), errors="coerce")
