"""modelo de otimização por divergência de kullback-leibler.

min_w sum_i w_i ln(w_i / p_i)  s.a. sum w_i = 1, w_i >= 0, w^T mu >= ρ

p_i é a distribuição de referência (ex.: 1/N, market cap). minimizar a
divergência de KL mantém a carteira o mais próxima possível da referência
(controle estrutural), equilibrando retorno e permanência. resolvido com
scipy.optimize.minimize (SLSQP).
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from ingenuo import carregar_retornos_simples, ponto_inicial, restricoes_padrao

P_PADRAO = (0.50, 0.25, 0.15, 0.10)

def _objetivo(w, p):
    return np.sum(w * np.log(w / p))


def _gradiente(w, p):
    return np.log(w / p) + 1.0


def pesos_kl(mu, rho, p=None, cov=None, sigma2_max=None, eps=1e-10):
    mu = np.asarray(mu, dtype=float)
    n = len(mu)

    if p is None:
        p = np.asarray(P_PADRAO, dtype=float)
        if len(p) != n:
            p = np.full(n, 1.0 / n)
    p = np.asarray(p, dtype=float)

    if rho > mu.max():
        raise ValueError(
            f"ρ {rho:.6f} > max(mu) {mu.max():.6f}: restrição de retorno infactível"
        )

    restricoes = restricoes_padrao(mu, rho, cov, sigma2_max)
    limites = [(eps, 1.0)] * n

    resultado = minimize(
        _objetivo,
        x0=ponto_inicial(mu, rho, cov, sigma2_max),
        args=(p,),
        jac=_gradiente,
        bounds=limites,
        constraints=restricoes,
        method="SLSQP",
        options={"ftol": 1e-12, "maxiter": 1000},
    )

    if not resultado.success:
        raise RuntimeError(f"otimização falhou: {resultado.message}")

    return resultado.x


def pesos_nomeados(mu_series, rho, p=None, cov=None, sigma2_max=None, eps=1e-10):
    mu = mu_series.to_numpy()
    w = pesos_kl(mu, rho, p, cov, sigma2_max, eps)
    return pd.Series(w, index=mu_series.index)

def carteira_base(mu_series, p=None, eps=1e-10):
    """solução MaxEnt irrestrita (sem restrição de retorno).

    para KL, a divergência mínima com restrição apenas de orçamento é
    w = p (a referência), independentemente de mu.
    """
    rho_base = float(mu_series.min() - 1.0)
    return pesos_nomeados(mu_series, rho_base, p=p, eps=eps)


def divergencia_kl(w, p=None):
    w = np.asarray(w, dtype=float)
    if p is None:
        p = np.asarray(P_PADRAO, dtype=float)
        if len(p) != len(w):
            p = np.full(len(w), 1.0 / len(w))
    return np.sum(w * np.log(w / np.asarray(p, dtype=float)))


if __name__ == "__main__":
    retornos = carregar_retornos_simples()
    mu = retornos.mean()
    r_uniforme = mu @ np.full(len(mu), 1.0 / len(mu))

    p_teste = {"dominância BTC (default)": None, "1/n": [0.25, 0.25, 0.25, 0.25]}
    for rho in [0.0, r_uniforme, 0.012, 0.014]:
        for nome, p in p_teste.items():
            pesos = pesos_nomeados(mu, rho, p)
            print(f"ρ = {rho:.4f} | p = {nome}:")
            print(pesos.round(6).to_string())
            print(
                f"  retorno carteira = {mu @ pesos.to_numpy():.6f} | "
                f"sum = {pesos.sum():.6f} | KL = {divergencia_kl(pesos, p):.4f}\n"
            )