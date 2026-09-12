"""modelo de otimização por entropia de tsallis.

max_w (1 - sum_i w_i^q) / (q - 1)  s.a. sum w_i = 1, w_i >= 0, w^T μ >= ρ

para q > 1, maximizar a entropia de tsallis equivale a minimizar sum_i w_i^q
(o fator 1/(q-1) é constante). resolvido numericamente com scipy.optimize.

parâmetro q controla a não-extensividade: q -> 1 recupera shannon;
q > 1 impõe penalidade mais forte sobre concentração (robustez a caudas pesadas).
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from ingenuo import carregar_retornos, ponto_inicial

def _objetivo(w, q):
    return np.sum(w**q)

def _gradiente(w, q):
    return q * w ** (q - 1.0)

def pesos_tsallis(mu, rho, q=2.0, eps=1e-10):
    mu = np.asarray(mu, dtype=float)
    n = len(mu)

    uniforme = np.full(n, 1.0 / n)

    if rho <= mu @ uniforme:
        return uniforme

    if rho > mu.max():
        raise ValueError(
            f"ρ {rho:.6f} > max(μ) {mu.max():.6f}: restrição de retorno infactível"
        )

    restricoes = [
        {"type": "eq", "fun": lambda w: np.sum(w) - 1.0},
        {"type": "ineq", "fun": lambda w: mu @ w - rho},
    ]
    limites = [(eps, 1.0)] * n

    resultado = minimize(
        _objetivo,
        x0=ponto_inicial(mu, rho),
        args=(q,),
        jac=_gradiente,
        bounds=limites,
        constraints=restricoes,
        method="SLSQP",
        options={"ftol": 1e-12, "maxiter": 1000},
    )

    if not resultado.success:
        raise RuntimeError(f"otimização falhou: {resultado.message}")

    return resultado.x

def pesos_nomeados(mu_series, rho, q=2.0, eps=1e-10):
    mu = mu_series.to_numpy()
    w = pesos_tsallis(mu, rho, q, eps)
    return pd.Series(w, index=mu_series.index)

def entropia_tsallis(w, q=2.0):
    w = np.asarray(w, dtype=float)
    return (1.0 - np.sum(w**q)) / (q - 1.0)

if __name__ == "__main__":
    retornos = carregar_retornos()
    mu = retornos.mean()
    r_uniforme = mu @ np.full(len(mu), 1.0 / len(mu))

    for rho in [0.0, r_uniforme, 0.012, 0.014]:
        for q in [1.01, 2.0, 3.0]:
            pesos = pesos_nomeados(mu, rho, q)
            print(f"rho = {rho:.4f} | q = {q:.2f}:")
            print(pesos.round(6).to_string())
            print(
                f"  retorno carteira = {mu @ pesos.to_numpy():.6f} | "
                f"sum = {pesos.sum():.6f} | H_q = {entropia_tsallis(pesos, q):.4f}\n"
            )