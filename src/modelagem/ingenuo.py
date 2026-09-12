"""modelo benchmark 1/n: alocação fixa e igualitária.

não envolve otimização: os pesos são determinísticos, w_i = 1/N
para todos os ativos. Satisfaz orçamento, não-negatividade e, quando
o portfólio igualitário atinge a meta, o retorno mínimo.
"""

from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
PASTA_PREP = RAIZ / "dados" / "prep"
ARQUIVO_RETORNOS = PASTA_PREP / "retornos-log-semanais.csv"
ARQUIVO_RETORNOS_SIMPLES = PASTA_PREP / "retornos-simples-semanais.csv"

def pesos_ingenuo(n_ativos):
    return np.full(n_ativos, 1.0 / n_ativos)

def pesos_nomeados(ativos):
    n = len(ativos)
    return pd.Series(pesos_ingenuo(n), index=ativos)

def ponto_inicial(mu, rho, cov=None, sigma2_max=None, eps=1e-4):
    """chute inicial robusto para o otimizador.

    quando a restrição de retorno rho é inativa, parte-se da carteira
    uniforme (o ótimo esperado). quando ativa, o ótimo tende a concentrar
    peso no ativo de maior retorno esperado — parte-se de um ponto
    concentrado, evitando falhas de linha de busca do SLSQP.

    quando há teto de variância, o ponto concentrado pode violá-lo; neste
    caso interpola-se linearmente entre a carteira uniforme (factível) e o
    ponto concentrado até o teto ser respeitado, mantendo um warm-start
    factível para todas as restrições.
    """
    mu = np.asarray(mu, dtype=float)
    n = len(mu)
    uniforme = np.full(n, 1.0 / n)
    if rho <= mu @ uniforme:
        return uniforme
    x = np.full(n, eps)
    x[np.argmax(mu)] = 1.0 - (n - 1) * eps

    if sigma2_max is not None and cov is not None:
        cov_arr = np.asarray(cov, dtype=float)
        if x @ cov_arr @ x > sigma2_max:
            lo, hi = 0.0, 1.0
            for _ in range(60):
                meio = 0.5 * (lo + hi)
                w = (1.0 - meio) * uniforme + meio * x
                if w @ cov_arr @ w <= sigma2_max:
                    lo = meio
                else:
                    hi = meio
            w = (1.0 - lo) * uniforme + lo * x
            return w
    return x

def retornos_portfolio(retornos, pesos):
    return retornos @ pesos

def esperado(retornos):
    return retornos.mean()

def carregar_retornos(arquivo=ARQUIVO_RETORNOS):
    return pd.read_csv(arquivo, index_col="Date", parse_dates=True)

def carregar_retornos_simples(arquivo=ARQUIVO_RETORNOS_SIMPLES):
    return pd.read_csv(arquivo, index_col="Date", parse_dates=True)

def restricoes_padrao(mu, rho, cov=None, sigma2_max=None):
    """constraints comuns a todos os otimizadores entrópicos.

    sempre presentes: orçamento (soma = 1) e retorno mínimo (≥ rho).
    opcionalmente, teto de variância σ² ≤ sigma2_max (do artigo).
    como o SLSQP do scipy trata retorno mínimo e variância como 'ineq'
    e o orçamento como 'eq', usa-se essa montagem central para evitar
    duplicação entre os modelos.
    """
    mu = np.asarray(mu, dtype=float)
    restricoes = [
        {"type": "eq", "fun": lambda w: np.sum(w) - 1.0},
        {"type": "ineq", "fun": lambda w: mu @ w - rho},
    ]
    if sigma2_max is not None:
        if cov is None:
            raise ValueError("sigma2_max exige a matriz de covariância cov.")
        cov_arr = np.asarray(cov, dtype=float)
        restricoes.append(
            {"type": "ineq", "fun": lambda w: sigma2_max - w @ cov_arr @ w}
        )
    return restricoes

if __name__ == "__main__":
    retornos = carregar_retornos()
    pesos = pesos_nomeados(retornos.columns)
    print("ativos:", list(pesos.index))
    print("\npesos 1/n:")
    print(pesos.to_string())
    print(f"\nsum pesos: {pesos.sum():.6f}")
    print(f"retorno esperado semanal da carteira: {esperado(retornos @ pesos):.6%}")