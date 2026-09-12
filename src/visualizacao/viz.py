"""visualização dos resultados do backtest.

gera figuras a partir dos arquivos salvos em `resultados/`:
  1. curvas acumuladas (riqueza relativa) de cada modelo
  2. drawdown ao longo do tempo
  3. retornos líquidos semanais dos modelos
  4. barras comparativas das métricas (acumulado, anualizado, Sharpe,
     Sortino, Max Drawdown)
  5. evolução dos pesos ao longo do tempo (por modelo)

as figuras são salvas em `resultados/graficos/`. para a evolução de pesos,
os pesos são recomputados via `backtest()` (não são persistidos em CSV).
"""

from pathlib import Path
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src" / "modelagem"))

from backtest import backtest
PASTA_RESULTADOS = RAIZ / "resultados"
PASTA_GRAFICOS = PASTA_RESULTADOS / "graficos"

ARQUIVO_RETORNOS = PASTA_RESULTADOS / "retornos-backtest.csv"
ARQUIVO_CURVAS = PASTA_RESULTADOS / "curvas-acumuladas.csv"
ARQUIVO_METRICAS = PASTA_RESULTADOS / "tabela-metricas.csv"
ARQUIVO_RETORNOS_PREP = RAIZ / "dados" / "prep" / "retornos-simples-semanais.csv"

PALETA = {
    "1/N": "#4C72B0",
    "shannon": "#DD8452",
    "tsallis": "#55A868",
    "renyi": "#C44E52",
    "wse": "#937860",
    "kl": "#8172B3",
}


def carregar_retornos(arquivo=ARQUIVO_RETORNOS):
    return pd.read_csv(arquivo, index_col="Date", parse_dates=True)


def carregar_curvas(arquivo=ARQUIVO_CURVAS):
    return pd.read_csv(arquivo, index_col="Date", parse_dates=True)


def carregar_metricas(arquivo=ARQUIVO_METRICAS):
    return pd.read_csv(arquivo, index_col=0)


def _estilo():
    mpl.rcParams.update(
        {
            "figure.dpi": 120,
            "axes.grid": True,
            "grid.alpha": 0.3,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "font.size": 10,
        }
    )


def grafico_curvas(curvas, arquivo):
    """curvas acumuladas (riqueza) por modelo, base log10 e eixo y relativo."""
    fig, ax = plt.subplots(figsize=(10, 5))
    for col in curvas.columns:
        ax.plot(curvas.index, curvas[col], label=col, color=PALETA[col], lw=1.6)
    ax.axhline(1.0, color="black", lw=0.8, alpha=0.5, ls="--")
    ax.set_yscale("log")
    ax.set_title("Evolução acumulada do portfólio (log)")
    ax.set_xlabel("Data")
    ax.set_ylabel("Riqueza relativa (base $t_0 = 1$)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(ncol=3, loc="upper left")
    fig.tight_layout()
    fig.savefig(arquivo, bbox_inches="tight")
    plt.close(fig)
    print(f"salvo em {arquivo}")


def grafico_drawdown(curvas, arquivo):
    """drawdown acumulado por modelo (área abaixo de zero)."""
    fig, ax = plt.subplots(figsize=(10, 5))
    for col in curvas.columns:
        dd = curvas[col] / curvas[col].cummax() - 1.0
        ax.plot(curvas.index, dd, label=col, color=PALETA[col], lw=1.4)
    ax.axhline(0.0, color="black", lw=0.8, alpha=0.5)
    ax.set_title("Drawdown acumulado por modelo")
    ax.set_xlabel("Data")
    ax.set_ylabel("Drawdown em relação ao pico")
    ax.legend(ncol=3, loc="lower left")
    fig.tight_layout()
    fig.savefig(arquivo, bbox_inches="tight")
    plt.close(fig)
    print(f"salvo em {arquivo}")


def grafico_retornos(retornos, arquivo):
    """retornos líquidos semanais por modelo (barra discreta)."""
    fig, ax = plt.subplots(figsize=(10, 5))
    for col in retornos.columns:
        ax.plot(retornos.index, retornos[col], label=col, color=PALETA[col], lw=0.8)
    ax.axhline(0.0, color="black", lw=0.8, alpha=0.5)
    ax.set_title("Retornos líquidos semanais por modelo")
    ax.set_xlabel("Data")
    ax.set_ylabel("Retorno semanal")
    ax.legend(ncol=3, loc="upper left")
    fig.tight_layout()
    fig.savefig(arquivo, bbox_inches="tight")
    plt.close(fig)
    print(f"salvo em {arquivo}")


def grafico_metricas(metricas, arquivo):
    """barras comparativas das métricas de cada modelo."""
    num = len(metricas)
    metricas_t = metricas.T
    n = len(metricas)
    linhas = int(np.ceil(n / 3))

    fig, axes = plt.subplots(linhas, 3, figsize=(12, 4 * linhas))
    axes = np.atleast_1d(axes).ravel()

    for i, (metrica, valores) in enumerate(metricas_t.iterrows()):
        ax = axes[i]
        cores = [PALETA[nome] for nome in metricas_t.columns]
        ax.bar(metricas_t.columns, valores, color=cores)
        ax.axhline(0.0, color="black", lw=0.8, alpha=0.5)
        ax.set_title(metrica)
        ax.tick_params(axis="x", rotation=30)

    for j in range(len(metricas_t), len(axes)):
        axes[j].set_visible(False)

    fig.suptitle("Métricas de desempenho por modelo", y=1.0)
    fig.tight_layout()
    fig.savefig(arquivo, bbox_inches="tight")
    plt.close(fig)
    print(f"salvo em {arquivo}")


def grafico_pesos(pesos_series, arquivo):
    """evolução dos pesos por modelo (áreas empilhadas)."""
    n = len(pesos_series)
    cols = list(next(iter(pesos_series.values())).columns)
    colunas = int(np.ceil(np.sqrt(n)))

    fig, axes = plt.subplots(
        n // colunas + (n % colunas > 0), colunas, figsize=(14, 3.2 * (1 + n // colunas))
    )
    axes = np.atleast_1d(axes).ravel()

    for i, (nome, pesos) in enumerate(pesos_series.items()):
        ax = axes[i]
        ax.stackplot(pesos.index, pesos.T, labels=cols, alpha=0.85)
        ax.set_title(nome)
        ax.set_ylim(0, 1)
        ax.margins(x=0)

    for j in range(n, len(axes)):
        axes[j].set_visible(False)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=len(cols), frameon=True)
    fig.suptitle("Evolução dos pesos por modelo", y=1.0)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.08)
    fig.savefig(arquivo, bbox_inches="tight")
    plt.close(fig)
    print(f"salvo em {arquivo}")


def gerar_todos():
    """gera todas as figuras a partir dos arquivos de `resultados/`."""
    PASTA_GRAFICOS.mkdir(parents=True, exist_ok=True)

    retornos = carregar_retornos()
    curvas = carregar_curvas()
    metricas = carregar_metricas()

    grafico_curvas(curvas, PASTA_GRAFICOS / "curvas-acumuladas.png")
    grafico_drawdown(curvas, PASTA_GRAFICOS / "drawdown.png")
    grafico_retornos(retornos, PASTA_GRAFICOS / "retornos-semanais.png")
    grafico_metricas(metricas, PASTA_GRAFICOS / "metricas.png")

    _, pesos_series = backtest(pd.read_csv(ARQUIVO_RETORNOS_PREP, index_col="Date", parse_dates=True))
    grafico_pesos(pesos_series, PASTA_GRAFICOS / "pesos.png")


if __name__ == "__main__":
    _estilo()
    gerar_todos()