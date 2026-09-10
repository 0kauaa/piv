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

def pesos_ingenuo(n_ativos):
    return np.full(n_ativos, 1.0 / n_ativos)

def pesos_nomeados(ativos):
    n = len(ativos)
    return pd.Series(pesos_ingenuo(n), index=ativos)

def retornos_portfolio(retornos, pesos):
    return retornos @ pesos

def esperado(retornos):
    return retornos.mean()

def carregar_retornos(arquivo=ARQUIVO_RETORNOS):
    return pd.read_csv(arquivo, index_col="Date", parse_dates=True)

if __name__ == "__main__":
    retornos = carregar_retornos()
    pesos = pesos_nomeados(retornos.columns)
    print("ativos:", list(pesos.index))
    print("\npesos 1/n:")
    print(pesos.to_string())
    print(f"\nsum pesos: {pesos.sum():.6f}")
    print(f"retorno esperado semanal da carteira: {esperado(retornos @ pesos):.6%}")