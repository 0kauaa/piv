import yfinance as yf
import pandas as pd
from pathlib import Path

CRIPTO = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"]
INICIO = "2020-01-01"
FIM = "2026-04-01"
INTERVALO = "1wk"
ARQUIVO = Path("dados") / "precos-semanais.csv"

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

def salvar(df, arquivo=ARQUIVO):
    arquivo.parent.mkdir(exist_ok=True)
    df.to_csv(arquivo)
    print(f"salvo em {arquivo}")

if __name__ == "__main__":
    precos = obter_precos()
    returns = retornos_semanais(precos)
    salvar(precos)
    salvar(returns, Path("dados") / "retornos-semanais.csv")
    print(precos)
    print("\nretornos semanais:")
    print(returns)