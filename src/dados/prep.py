"""pré-processamento dos dados brutos de criptoativos.

1. alinhamento temporal (resample semanal + forward fill + dropna)
2. uso do preço ajustado (Close ajustado do yfinance)
3. retornos logarítmicos
4. outliers preservados (sem winsorização)
"""

from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
DADOS = RAIZ / "dados"
PASTA_BRUTOS = DADOS / "brutos"
PASTA_PREP = DADOS / "prep"

ARQUIVO_BRUTO = PASTA_BRUTOS / "precos-semanais.csv"
ARQUIVO_ALINHADO = PASTA_PREP / "precos-alinhados-semanais.csv"
ARQUIVO_RETORNOS = PASTA_PREP / "retornos-log-semanais.csv"

CRIPTO = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"]
FREQ_SEMANAL = "W-FRI"

def carregar_bruto(arquivo=ARQUIVO_BRUTO):
    preco = pd.read_csv(arquivo, index_col="Date", parse_dates=True)
    return preco.sort_index()

def alinhar(preco, freq=FREQ_SEMANAL):
    """alinha todos os ativos ao mesmo índice semanal.

    o resample com 'last' captura o último preço válido da semana; o
    forward fill replica o último preço conhecido para lacunas; o dropna
    remove, de forma sincronizada, semanas sem cobertura de algum ativo.
    """
    alinhado = preco.resample(freq).last()
    alinhado = alinhado.ffill()
    alinhado = alinhado.dropna(how="any")
    return alinhado

def retornos_log(preco):
    """retornos logarítmicos: ln(P_t / P_{t-1})."""
    return np.log(preco / preco.shift(1)).dropna()

def padronizar_colunas(df):
    return df[CRIPTO]

def salvar(df, arquivo):
    arquivo.parent.mkdir(exist_ok=True)
    df.to_csv(arquivo)
    print(f"salvo em {arquivo}")

def resumo(preco, prefixo=""):
    print(f"{prefixo}periodo: {preco.index.min().date()} a {preco.index.max().date()}")
    print(f"{prefixo}observacoes: {len(preco)}")
    print(f"{prefixo}ativo(s) ausente(s): {preco.columns[preco.isna().any()].tolist()}")

if __name__ == "__main__":
    bruto = carregar_bruto()
    print("dados brutos:")
    resumo(bruto)
    print(f"linhas: {bruto.shape[0]} | colunas: {bruto.shape[1]}\n")

    alinhado = padronizar_colunas(alinhar(bruto))
    print("dados alinhados:")
    resumo(alinhado)
    print(f"lacunas restantes: {int(alinhado.isna().sum().sum())}\n")
    salvar(alinhado, ARQUIVO_ALINHADO)

    retornos = retornos_log(alinhado)
    print("retornos logaritmicos:")
    resumo(retornos)
    salvar(retornos, ARQUIVO_RETORNOS)