# Registro Metodológico do Projeto

> Protocolo de ações para a fase de escrita do artigo.
> Toda ação de implementação solicitada será registrada aqui a partir de 10/09.

---

## 1. Registro de Ações (Diário Metodológico)

> Cada entrada descreve **o que** foi feito, **como** foi feito e **quais escolhas**
> foram tomadas, servindo de base narrativa para a seção metodológica do artigo.

### 1.1. Definição da metodologia de implementação

- **Data:** 10/09
- **O que:** Deﬁnição do plano de implementação do projeto, cobrindo as quatro etapas de pesquisa: aquisição de dados, modelagem matemática, arquitetura de backtest e métricas de avaliação.
- **Como:** Documentado em `notas/projeto.md` a partir das especificações do usuário.
- **Escolhas tomadas:** O escopo de estratégias passou a incluir também o clássico **Markowitz** (mínima variância) além dos modelos entrópicos; o *backtest* seria baseado em **rebalanceamento periódico** com janela móvel para evitar viés de *look-ahead*; as métricas escolhidas foram retorno acumulado/anualizado (Frente A), Max Drawdown e Sortino (Frente B), e Sharpe (eficiência geral).
- **Evidência:** este arquivo (reformulado posteriormente).

### 1.2. Implementação do pré-processamento (`src/dados`)

- **Data:** 10/09
- **O que:** Criação do pipeline de pré-processamento dos dados brutos de criptoativos.
- **Como:** O módulo `prep.py` executa, em ordem: (i) resample semanal `W-FRI` capturando o último preço válido da semana; (ii) *forward fill* para lacunas pontuais; (iii) *dropna* sincronizado para semanas sem cobertura de algum ativo; (iv) cálculo de retornos logarítmicos $\ln(P_t/P_{t-1})$.
- **Escolhas tomadas:**
  - **Retornos logarítmicos** em vez de simples — aditividade temporal e melhor tratamento estatístico para as estimativas de $\mu$ e covariância.
  - **Preço ajustado** (`auto_adjust=True` do yfinance) — mitiga correções fantasma de splits na API.
  - **Outliers preservados** (sem winsorização) — flash crashes são o objeto da análise de risco de cauda; limpar as quedas anularia o teste de estresse de Tsallis/Rényi.
  - **Alinhamento por sexta-feira (`W-FRI`)** como anchor semanal da amostra.
- **Evidência:** `src/dados/prep.py`; saídas em `dados/prep/precos-alinhados-semanais.csv` e `dados/prep/retornos-log-semanais.csv`. O alinhamento cortou as semanas iniciais (SOL sem dados em 01/2020), iniciando a série em 04/2020 com 313 observações.

### 1.3. Implementação do modelo benchmark 1/N

- **Data:** 10/09
- **O que:** Implementação do portfólio ingênuo de pesos iguais.
- **Como:** `src/modelagem/ingenuo.py` define pesos determinísticos $w_i = 1/N$ (sem otimização), com funções para retorno do portfólio ($w^T r_t$) e retorno esperado ($w^T \mu$), lendo a série processada de retornos log.
- **Escolha tomada:** O 1/N é o **benchmark base** do estudo, conforme a narrativa do projeto — e não uma estratégia otimizada. Mantida a ordem canônica dos ativos (BTC, ETH, SOL, BNB).
- **Validado:** soma dos pesos = 1,000000; retorno esperado semanal da carteira ≈ 1,05%.
- **Evidência:** `src/modelagem/ingenuo.py`.

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

- [X] Aquisição e pré-processamento dos dados (janela 01/04/2020–01/03/2025).
- [ ] Implementação das funções objetivo (1/N, Markowitz, Shannon, Tsallis, Rényi, KL).
- [ ] Arquitetura do backtest com janela móvel e rebalanceamento periódico.
- [ ] Cálculo das métricas de desempenho (Frente A, Frente B e eficiência geral).
- [ ] Analise dos resultados obtidos.
- [ ] Redação do artigo.
