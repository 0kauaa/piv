# Registro Metodológico do Projeto

> Protocolo de ações para a fase de escrita do artigo.
> Toda ação de implementação solicitada será registrada aqui a partir de 10/09.

---

## 1. Linha do Tempo de Ações

| # | Data  | Ação                                                                                                                                                                      | Evidência        |
| - | ----- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| 1 | 10/09 | Definição da metodologia de implementação: dados, funções objetivo (inclui Markowitz), arquitetura de backtest com rebalanceamento e métricas (MDD, Sortino, Sharpe) | este arquivo, §6 |

---

## 2. Contexto e Motivação

A otimização tradicional de portfólios (Markowitz, média-variância) falha em criptoativos
devido à alta volatilidade, assimetria e distribuições de retornos com caudas pesadas.

Este projeto adota a **Teoria da Informação** (entropia) como regulador estrutural de
diversificação, seguindo o arcabouço de Dedu & Șerban (*Unified Maximum Entropy Framework*),
mas com abordagem **pragmática e empírica**: testar as formulações entrópicas contra dados
reais, usando $1/N$ como benchmark.

---

## 3. Decisões Metodológicas Tomadas

### 3.1. Referência base

- **Artigo:** *Entropy-Based Portfolio Optimization in Cryptocurrency Markets: A Unified
  Maximum Entropy Framework* (Dedu & Șerban).
- **Papel:** fundamento teórico do diário (registro) metodológico; o projeto não reescreve
  a teoria, mas valida empiricamente os modelos derivados do MaxEnt.

### 3.2. Escopo de comparação

- **Benchmark:** $1/N$ (pesos iguais).
- **Modelos entrópicos:** Shannon, Tsallis, Weighted Shannon, Rényi, Kullback-Leibler.

### 3.3. Estrutura de avaliação

- **Frente A (Upside):** retorno acumulado e retorno anualizado — captura de ganho.
- **Frente B (Downside):** Max Drawdown, resiliência em bear markets, risco de cauda —
  proteção de capital.

---

## 4. Dados

| Item                  | Definição                                                    |
| --------------------- | -------------------------------------------------------------- |
| Ativos                | BTC, ETH, SOL, BNB                                             |
| Fonte                 | yfinance (`dados.py`)                                        |
| Frequência           | semanal                                                        |
| Janela histórica     | 2020–2025 (estimação de parâmetros e otimização)         |
| Janela de avaliação | 2026 (backtest fora da amostra)                                |
| Arquivos              | `dados/precos-semanais.csv`, `dados/retornos-semanais.csv` |

---

## 5. Modelos a Implementar

Detalhamento completo em `notas/modelos.md`. Resumo das restrições comuns:

$$
\sum_i w_i = 1, \quad w_i \geq 0, \quad w^T\mu \geq R_{min}
$$

| Modelo            | Objetivo                                                   |
| ----------------- | ---------------------------------------------------------- |
| $1/N$           | Benchmark ingênuo                                         |
| Shannon           | $\max -\sum w_i \ln w_i$                                 |
| Tsallis ($q=2$) | $\max \frac{-\sum w_i^q}{q-1}$                           |
| Rényi            | $\max \frac{1}{1-\alpha}\ln\left(\sum w_i^\alpha\right)$ |
| Kullback-Leibler  | $\min \sum w_i \ln(w_i/p_i)$                             |

---

## 6. Checklist de Implementação

- [ ] Aquisição e pré-processamento dos dados (janela 01/04/2020–01/03/2025).
- [ ] Implementação das funções objetivo (1/N, Markowitz, Shannon, Tsallis, Rényi, KL).
- [ ] Arquitetura do backtest com janela móvel e rebalanceamento periódico.
- [ ] Cálculo das métricas de desempenho (Frente A, Frente B e eficiência geral).
- [ ] Analise dos resultados obtidos.
- [ ] Redação do artigo.
