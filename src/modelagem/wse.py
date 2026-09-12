"""modelo de otimização por entropia de shannon ponderada (wse).

max_w (-sum_i u_i w_i ln w_i)  s.a. sum w_i = 1, w_i >= 0, w^T mu >= ρ

u_i > 0 são pesos informacionais (prioridades) por ativo. quando u_i = 1
para todo i, recupera a entropia de shannon clássica. resolvido com
scipy.optimize.minimize (SLSQP), minimizando sum_i u_i w_i ln w_i.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from ingenuo import carregar_retornos, ponto_inicial


def _objetivo(w, u):
    return np.sum(u * w * np.log(w))


def _gradiente(w, u):
    return u * (np.log(w) + 1.0)


def pesos_wse(mu, rho, u=None, eps=1e-10):
    mu = np.asarray(mu, dtype=float)
    n = len(mu)

    if u is None:
        u = np.ones(n)
    u = np.asarray(u, dtype=float)

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
        args=(u,),
        jac=_gradiente,
        bounds=limites,
        constraints=restricoes,
        method="SLSQP",
        options={"ftol": 1e-12, "maxiter": 1000},
    )

    if not resultado.success:
        raise RuntimeError(f"otimização falhou: {resultado.message}")

    return resultado.x


def pesos_nomeados(mu_series, rho, u=None, eps=1e-10):
    mu = mu_series.to_numpy()
    w = pesos_wse(mu, rho, u, eps)
    return pd.Series(w, index=mu_series.index)


def entropia_wse(w, u=None):
    w = np.asarray(w, dtype=float)
    if u is None:
        u = np.ones(len(w))
    return -np.sum(np.asarray(u, dtype=float) * w * np.log(w))


if __name__ == "__main__":
    retornos = carregar_retornos()
    mu = retornos.mean()
    r_uniforme = mu @ np.full(len(mu), 1.0 / len(mu))
    ativos = retornos.columns

    for rho in [0.0, r_uniforme, 0.012, 0.014]:
        u_teste = {"uniforme": None, "btc-eth favoritos": [3.0, 2.0, 1.0, 1.0]}
        for nome, u in u_teste.items():
            pesos = pesos_nomeados(mu, rho, u)
            print(f"ρ = {rho:.4f} | u = {nome}:")
            print(pesos.round(6).to_string())
            print(
                f"  retorno carteira = {mu @ pesos.to_numpy():.6f} | "
                f"sum = {pesos.sum():.6f} | H_w = {entropia_wse(pesos, u):.4f}\n"
            )