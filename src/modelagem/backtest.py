"""backtest walk-forward com janela móvel.

a cada semana de corte:
    1. recorta a janela de treinamento (estimation window)
    2. estima mu e a matriz de covariância na janela
    3. resolve o otimizador de cada modelo sujeito a
       sum w = 1, w >= 0, w^T mu >= rho, w^T Sigma w <= sigma2_max
    4. fixa os pesos w* e aplica no período out-of-sample seguinte

o avanco e semanal (rolling): descarta a semana mais antiga, incorpora a
mais recente e recalcula. retornos liquido de custos de transacao
proporcionais a variacao absoluta dos pesos (|Delta w|).

a meta de retorno rho e dinâmica e relativa ao regime: exigir um percentual
fixo tornaria a restricao infactivel em bear markets (como diagnosticado na
auditoria). aqui rho e definido como uma fracao do retorno que o proprio
benchmark 1/N obteve na janela de treinamento — sem piso em taxa livre de
risco, para que a meta acompanhe o mercado inclusive quando negativa e a
restricao de retorno permaneça factivel em todos os ciclos (a infactibilidade
restante vem só do teto de variância, operado em cenários separados).

todos os retornos usados sao aritmeticos (simples): a estimacao de mu, a
matriz de covariância, a execucao do portfólio e a acumulacao de capital.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from ingenuo import pesos_nomeados as pesos_ingenuo
from shannon import pesos_nomeados as pesos_shannon, carteira_base as base_shannon
from tsallis import pesos_nomeados as pesos_tsallis, carteira_base as base_tsallis
from renyi import pesos_nomeados as pesos_renyi, carteira_base as base_renyi
from wse import pesos_nomeados as pesos_wse, carteira_base as base_wse
from kl import pesos_nomeados as pesos_kl, carteira_base as base_kl

RAIZ = Path(__file__).resolve().parents[2]
PASTA_PREP = RAIZ / "dados" / "prep"
PASTA_RESULTADOS = RAIZ / "resultados"
ARQUIVO_RETORNOS = PASTA_PREP / "retornos-simples-semanais.csv"

MODELOS = {
    "1/N": pesos_ingenuo,
    "shannon": pesos_shannon,
    "tsallis": pesos_tsallis,
    "renyi": pesos_renyi,
    "wse": pesos_wse,
    "kl": pesos_kl,
}

BASES = {
    "1/N": lambda mu: pesos_ingenuo(mu.index),
    "shannon": base_shannon,
    "tsallis": base_tsallis,
    "renyi": base_renyi,
    "wse": base_wse,
    "kl": base_kl,
}


def carregar_retornos(arquivo=ARQUIVO_RETORNOS):
    return pd.read_csv(arquivo, index_col="Date", parse_dates=True)


def meta_retorno(mu, fator=0.5, rf_semanal=None):
    """rho dinâmico, relativo ao benchmark 1/N da janela.

    rho = retorno_1N + fator * (max(mu) - retorno_1N),
    onde retorno_1N = mu @ w_1N e w_1N = 1/N.

    o alvo fica entre o retorno esperado do benchmark e o melhor ativo da
    janela: (i) sempre factivel quanto a retorno (<= max(mu)); (ii) vinculante
    quando ha dispersao (> retorno_1N); (iii) adapta-se ao regime — em bear
    markets os dois extremos sao negativos e a meta acompanha o mercado,
    mantendo o otimizador ativo (diferencia a frente B nos periodos
    estressados). sem piso em rf: o piso transformava bears profundos em
    30+ janelas infactiveis (rho=0 > max(mu)<0) com colapso em carteira-base.
    rf_semanal e mantido na assinatura por compatibilidade, mas ignorado.
    """
    retorno_1n = mu @ np.full(len(mu), 1.0 / len(mu))
    excesso = mu.max() - retorno_1n
    return retorno_1n + fator * excesso


def _resolver(nome, mu_series, rho, cov, sigma2_max):
    if nome == "1/N":
        return pesos_ingenuo(mu_series.index)
    try:
        if nome == "shannon":
            return pesos_shannon(mu_series, rho, cov=cov, sigma2_max=sigma2_max)
        if nome == "tsallis":
            return pesos_tsallis(mu_series, rho, cov=cov, sigma2_max=sigma2_max)
        if nome == "renyi":
            return pesos_renyi(mu_series, rho, cov=cov, sigma2_max=sigma2_max)
        if nome == "wse":
            return pesos_wse(mu_series, rho, cov=cov, sigma2_max=sigma2_max)
        if nome == "kl":
            return pesos_kl(mu_series, rho, cov=cov, sigma2_max=sigma2_max)
    except (ValueError, RuntimeError):
        return BASES[nome](mu_series)
    raise ValueError(f"modelo desconhecido: {nome}")


def pesos_iniciais(ativos):
    return pd.Series(1.0 / len(ativos), index=ativos)


def backtest(
    retornos,
    janela=52,
    fator_meta=0.5,
    rf_semanal=0.0,
    fator_var=2.0,
    custo=0.001,
    modelos=None,
):
    """executa o backtest e retorna (retornos_liquidos, pesos_series).

    retornos_liquidos: DataFrame com o retorno semanal out-of-sample de cada
    modelo, indexado pelas datas das semanas de teste.
    pesos_series: dict nome -> DataFrame com os pesos aplicados a cada semana.

    rho dinâmico: meta_retorno(mu, fator_meta) — sem piso em rf, pode ser
    negativo em bears para preservar factibilidade (rf_semanal mantido na
    assinatura por compatibilidade, mas ignorado).
    restrição de variância: sigma2_max = fator_var * variância do 1/N na
    janela. o default fator_var=2.0 admite risco até o dobro do benchmark nas
    janelas onde a dispersão justifica concentração (cenário upside da Frente A;
    o cenário downside com fator_var<=1.0 e avaliado em separado — ver notas).
    a calibração antiga com piso rf=0 mostrava fator_var=1.0 com ~2/3 das
    janelas infactíveis; sem o piso, a factibilidade de retorno e total e a
    infactibilidade restante vem só da variância.
    """
    modelos = modelos or list(MODELOS)

    serie_por_modelo = {nome: [] for nome in modelos}
    pesos_por_modelo = {nome: [] for nome in modelos}
    pesos_ant = {nome: pesos_iniciais(retornos.columns) for nome in modelos}

    for t in range(janela, len(retornos)):
        treino = retornos.iloc[t - janela : t]
        mu = treino.mean()
        cov = treino.cov()

        w_1n = pesos_iniciais(retornos.columns)
        sigma2_max = fator_var * float(w_1n @ cov @ w_1n)
        rho = meta_retorno(mu, fator_meta, rf_semanal)

        for nome in modelos:
            w = _resolver(nome, mu, rho, cov, sigma2_max)
            w = w.reindex(retornos.columns).fillna(0.0)

            custo_tx = custo * np.abs(w.to_numpy() - pesos_ant[nome].to_numpy()).sum()

            r_out = retornos.iloc[t] @ w

            serie_por_modelo[nome].append(r_out - custo_tx)
            pesos_por_modelo[nome].append(w)
            pesos_ant[nome] = w

    datas = retornos.index[janela:]
    retornos_liquidos = pd.DataFrame(serie_por_modelo, index=datas)

    pesos_series = {
        nome: pd.DataFrame(pesos_por_modelo[nome], index=datas)
        for nome in modelos
    }

    return retornos_liquidos, pesos_series


def curva_acumulada(retornos):
    return (1.0 + retornos).cumprod()


def metricas(retornos, rf=0.0):
    """calcula retorno acumulado/anualizado, sharpe, sortino e max drawdown.

    retornos: DataFrame com retornos semanais por coluna (estratégia).
    """
    n_semanas = 52
    acumulado = (1.0 + retornos).prod() - 1.0
    medidas = (1.0 + retornos).prod() ** (n_semanas / max(len(retornos), 1)) - 1.0

    vol = retornos.std() * np.sqrt(n_semanas)
    sharpe = (medidas - rf) / vol

    alvo = retornos[retornos < 0].std()
    desvio_baixa_anual = alvo * np.sqrt(n_semanas)
    sortino = (medidas - rf) / desvio_baixa_anual

    mdd = mdd_de(retornos)

    return pd.DataFrame(
        {
            "retorno_acumulado": acumulado,
            "retorno_anualizado": medidas,
            "vol_anual": vol,
            "sharpe": sharpe,
            "sortino": sortino,
            "max_drawdown": mdd,
        }
    )


def mdd_de(retornos):
    acum = (1.0 + retornos).cumprod()
    pico = acum.cummax()
    drawdown = acum / pico - 1.0
    return drawdown.min()


REGIMES = [
    # blocos do OOS espelhando os regimes do artigo + cauda final.
    # expansão: fim do bull 2021; stress: bear 2022; recuperação: 2023–2025-03;
    # cauda: 2025-04 em diante (topo e correção recente).
    ("expansao", "2021-04-16", "2021-12-31"),
    ("stress", "2022-01-01", "2022-12-31"),
    ("recuperacao", "2023-01-01", "2025-03-31"),
    ("cauda", "2025-04-01", "2026-04-03"),
]


def metricas_por_regime(retornos_liquidos):
    """métricas de cada modelo dentro de cada bloco de regime.

    retorna DataFrame longo [regime, modelo, *métricas, n_semanas].
    o max_drawdown aqui é intra-bloco (a partir de base 1 no início do bloco),
    não o global — serve à Frente B condicional, não ao MDD total.
    o retorno anualizado em blocos curtos extrapola (52/n); ver n_semanas.
    """
    linhas = []
    for regime, inicio, fim in REGIMES:
        bloco = retornos_liquidos.loc[inicio:fim]
        if bloco.empty:
            continue
        tab = metricas(bloco)
        for modelo in tab.index:
            linhas.append(
                {
                    "regime": regime,
                    "modelo": modelo,
                    "n_semanas": len(bloco),
                    **tab.loc[modelo].to_dict(),
                }
            )
    return pd.DataFrame(linhas).set_index(["regime", "modelo"]).sort_index()


def salvar(df, arquivo):
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(arquivo)
    print(f"salvo em {arquivo}")


CENARIOS = {
    # nome: fator_var. agressivo = teto permissivo (Frente A, captura de ganho);
    # conservador = teto restritivo (Frente B, resiliência em stress).
    # mesmo rho nos dois (fator_meta=0.5): a diferença vem só do teto, para que
    # o artigo compare o comportamento do backtest nos dois tetos. risco e ganho
    # são eixos separados — o conservador tende ao colapso em carteira-base
    # (achado empírico, não falha): documentar a taxa de fallback, não escondê-la.
    "agressivo": 2.0,
    "conservador": 1.0,
}

SUFIJO_ARQUIVO = {
    # agressivo mantém os nomes canônicos (compatibilidade); conservador usa sufixo.
    "agressivo": "",
    "conservador": "-var1.0",
}


if __name__ == "__main__":
    retornos = carregar_retornos()

    for nome, fvar in CENARIOS.items():
        suf = SUFIJO_ARQUIVO[nome]
        retornos_liquidos, pesos_series = backtest(retornos, fator_var=fvar)

        curvas = curva_acumulada(retornos_liquidos)
        tabela = metricas(retornos_liquidos)

        print(f"\n===== cenário {nome} (fator_var={fvar}) =====")
        print(retornos_liquidos.head())
        print("\ntabela de metricas:")
        print(tabela.round(4).to_string())
        print("\ncurva acumulada (final):")
        print(curvas.iloc[-1].round(4).to_string())

        por_regime = metricas_por_regime(retornos_liquidos)
        print("\nmetricas por regime (acumulado / sharpe / mdd intra-bloco):")
        print(por_regime[["retorno_acumulado", "sharpe", "max_drawdown"]].round(4).to_string())

        salvar(retornos_liquidos, PASTA_RESULTADOS / f"retornos-backtest{suf}.csv")
        salvar(curvas, PASTA_RESULTADOS / f"curvas-acumuladas{suf}.csv")
        salvar(tabela, PASTA_RESULTADOS / f"tabela-metricas{suf}.csv")
        salvar(por_regime, PASTA_RESULTADOS / f"tabela-metricas-por-regime{suf}.csv")