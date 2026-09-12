"""modelo de otimização por entropia de rényi.

max_w 1/(1-α) ln(sum_i w_i^α)  s.a. sum w_i = 1, w_i >= 0, w^T mu >= ρ

a entropia de rényi generaliza shannon/index de diversidade,
parametrizada por α. o objetivo é minimizado diretamente (menos entropia)
com scipy.optimize.minimize (SLSQP).
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from ingenuo import carregar_retornos, ponto_inicial


def _objetivo(w, alfa):
    soma = np.sum(w**alfa)
    return -1.0 / (1.0 - alfa) * np.log(soma)


def _gradiente(w, alfa):
    soma = np.sum(w**alfa)
    return -alfa * w ** (alfa - 1.0) / ((1.0 - alfa) * soma)


def pesos_renyi(mu, rho, alfa=2.0, eps=1e-10):
    mu = np.asarray(mu, dtype=float)
    n = len(mu)

    uniforme = np.full(n, 1.0 / n)

    if rho <= mu @ uniforme:
        return uniforme

    if rho > mu.max():
        raise ValueError(
            f"ρ {rho:.6f} > max(mu) {mu.max():.6f}: restrição de retorno infactível"
        )

    restricoes = [
        {"type": "eq", "fun": lambda w: np.sum(w) - 1.0},
        {"type": "ineq", "fun": lambda w: mu @ w - rho},
    ]
    limites = [(eps, 1.0)] * n

    resultado = minimize(
        _objetivo,
        x0=ponto_inicial(mu, rho),
        args=(alfa,),
        jac=_gradiente,
        bounds=limites,
        constraints=restricoes,
        method="SLSQP",
        options={"ftol": 1e-12, "maxiter": 1000},
    )

    if not resultado.success:
        raise RuntimeError(f"otimização falhou: {resultado.message}")

    return resultado.x


def pesos_nomeados(mu_series, rho, alfa=2.0, eps=1e-10):
    mu = mu_series.to_numpy()
    w = pesos_renyi(mu, rho, alfa, eps)
    return pd.Series(w, index=mu_series.index)


def entropia_renyi(w, alfa=2.0):
    w = np.asarray(w, dtype=float)
    return 1.0 / (1.0 - alfa) * np.log(np.sum(w**alfa))


if __name__ == "__main__":
    retornos = carregar_retornos()
    mu = retornos.mean()
    r_uniforme = mu @ np.full(len(mu), 1.0 / len(mu))

    for rho in [0.0, r_uniforme, 0.012, 0.014]:
        for alfa in [1.01, 2.0, 3.0]:
            pesos = pesos_nomeados(mu, rho, alfa)
            print(f"ρ = {rho:.4f} | alfa = {alfa:.2f}:")
            print(pesos.round(6).to_string())
            print(
                f"  retorno carteira = {mu @ pesos.to_numpy():.6f} | "
                f"sum = {pesos.sum():.6f} | H_α = {entropia_renyi(pesos, alfa):.4f}\n"
            )