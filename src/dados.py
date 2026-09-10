import yfinance as yf
import pandas as pd
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PASTA_BRUTOS = RAIZ / "dados" / "brutos"

CRIPTO = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"]
INICIO = "2020-01-01"
FIM = "2026-04-01"
INTERVALO = "1wk"
ARQUIVO_PRECOS = PASTA_BRUTOS / "precos-semanais.csv"
ARQUIVO_RETORNOS = PASTA_BRUTOS / "retornos-semanais.csv"

def obter_precos(tickers=CRIPTO, inicio=INICIO, fim=FIM, intervalo=INTERVALO):
    preco = yf.download(
        tickers,
        start=inicio,
        end=fim,
        interval=intervalo,
        progress=False,
        auto_adjust=True,
    )
    if isinstance(preco.columns, pd.MultiIndex):
        preco = preco["Close"]
    return preco

def retornos_semanais(precos):
    return precos.pct_change().dropna()

def salvar(df, arquivo):
    arquivo.parent.mkdir(exist_ok=True)
    df.to_csv(arquivo)
    print(f"salvo em {arquivo}")

if __name__ == "__main__":
    precos = obter_precos()
    returns = retornos_semanais(precos)
    salvar(precos, ARQUIVO_PRECOS)
    salvar(returns, ARQUIVO_RETORNOS)
    print(precos)
    print("\nretornos semanais:")
    print(returns)