"""modelo de otimização por entropia de shannon.

max_w (-sum_i w_i ln w_i)  s.a. sum w_i = 1, w_i >= 0, w^T mu >= α

resolvido numericamente com scipy.optimize.minimize (SLSQP). o problema é
convexo: minimizar sum_i w_i ln w_i equivale a maximizar a entropia.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from ingenuo import carregar_retornos

def _objetivo(w):
    return np.sum(w * np.log(w))

def _gradiente(w):
    return np.log(w) + 1.0

def pesos_shannon(mu, alpha, eps=1e-10):
    mu = np.asarray(mu, dtype=float)
    n = len(mu)

    uniforme = np.full(n, 1.0 / n)

    if alpha <= mu @ uniforme:
        return uniforme

    if alpha > mu.max():
        raise ValueError(
            f"α {alpha:.6f} > max(μ) {mu.max():.6f}: restrição de retorno infactível"
        )

    restricoes = [
        {"type": "eq", "fun": lambda w: np.sum(w) - 1.0},
        {"type": "ineq", "fun": lambda w: mu @ w - alpha},
    ]
    limites = [(eps, 1.0)] * n

    resultado = minimize(
        _objetivo,
        x0=uniforme,
        jac=_gradiente,
        bounds=limites,
        constraints=restricoes,
        method="SLSQP",
        options={"ftol": 1e-12, "maxiter": 1000},
    )

    if not resultado.success:
        raise RuntimeError(f"otimização falhou: {resultado.message}")

    return resultado.x

def pesos_nomeados(mu_series, alpha, eps=1e-10):
    mu = mu_series.to_numpy()
    w = pesos_shannon(mu, alpha, eps)
    return pd.Series(w, index=mu_series.index)

if __name__ == "__main__":
    retornos = carregar_retornos()
    mu = retornos.mean()
    r_uniforme = mu @ np.full(len(mu), 1.0 / len(mu))

    for alpha in [0.0, r_uniforme, 0.012, 0.014]:
        pesos = pesos_nomeados(mu, alpha)
        print(f"alpha = {alpha:.4f}:")
        print(pesos.round(6).to_string())
        print(f"  retorno carteira = {mu @ pesos.to_numpy():.6f} | sum = {pesos.sum():.6f}\n")