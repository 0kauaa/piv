# Proposta de Projeto de Artigo: Otimização de Portfólio em Criptomoedas via Teoria da Informação

---

## 1. Contextualização e Diagnóstico

A otimização tradicional de portfólios baseada no modelo de **Markowitz (Média-Variância)** falha flagrantemente no mercado de criptoativos. Devido à alta volatilidade, assimetria (*skewness*) e distribuições de retornos com caudas pesadas (*fat-tailed*), as premissas paramétricas do Markowitz desmoronam, gerando erros severos de estimação e portfólios hiperconcentrados.

Seguindo a premissa de Silvia Dedu e Florentin Șerban (*Entropy-Based Portfolio Optimization in Cryptocurrency Markets*), este projeto adota a **Entropia** como um regulador estrutural e livre de premissas rígidas (*distribution-free*), garantindo uma diversificação geométrica natural por meio da Teoria da Informação.

---

## 2. A Narrativa do Projeto

Diferente do artigo original, que deriva matematicamente o arcabouço unificado de Máxima Entropia (MaxEnt) comparando Shannon, Tsallis e Weighted Shannon em análise estática por regime, este projeto usa o estudo como **base fundacional** e o estende para uma **extensão dinâmica com backtest**.

O foco não é reescrever a teoria, mas sim **testar se o arcabouço entrópico faz sentido na prática**: colocar as formulações à prova em walk-forward fora da amostra, com custos de transação e rebalanceamento semanal, utilizando o clássico portfólio ingênuo **$1/N$ (pesos iguais) como benchmark base**. A réplica limita-se aos fundamentos (ativos, entropias do artigo, restrições de orçamento/retorno/variância); a inovação é a operação dinâmica.

A narrativa do artigo gira em torno da utilidade prática: *a regularização entrópica sustenta diversificação estável fora da amostra, inclusive em stress?*

---

## 3. Metodologia e Escopo de Comparação

O projeto compara o desempenho histórico (*backtest* walk-forward) das seguintes estratégias na mesma base de dados de criptoativos:

* **Benchmark Base:** Portfólio Ingênuo ($1/N$).
* **Núcleo réplica (do artigo):**
  * Entropia de Shannon
  * Entropia de Tsallis ($q=2$)
  * Entropia Ponderada de Shannon (*Weighted Shannon*)
* **Extensão dinâmica (inovação do projeto):**
  * Entropia de Rényi ($\alpha=3.0$) — generalização fora do MaxEnt unificado, sensibilidade alternativa à concentração
  * Divergência de Kullback-Leibler (prior $p$) — controle estrutural por distância a uma referência, não maximização de entropia

---

## 4. Dados (via yfinance)

Cryptos: BTC, ETH, SOL, BNB — semanais (`W-FRI`).

**Warm-up (estimação):** 2020–2021 (janela inicial de 52 semanas).
**Backtest out-of-sample:** 2021-04-16 a 2026-04-03 (260 semanas, walk-forward semanal com custos).

---

## 5. O Coração Analítico: "Ganho" vs. "Perda"

Para fugir de análises superficiais de rentabilidade, o estudo divide a avaliação em duas frentes complementares. A motivação é que **minimizar risco não é maximizar ganho, e vice-versa** — por isso o projeto opera os dois tetos de variância em cenários separados (permissivo p/ Frente A, restritivo p/ Frente B), sem misturá-los.

### Frente A: Agressividade e Captura de Ganho (Upside)

* **Objetivo:** Avaliar qual formulação sustenta diversificação estável com captura de alta em *bull markets*, sob teto de variância permissivo.
* **Foco:** Retorno acumulado total e Retorno Anualizado (global).

### Frente B: Resiliência em Stress (Downside) — principal inovação empírica

* **Objetivo:** Motivação empírica da extensão: testar se a regularização entrópica mantém alocações interpretáveis em *bear markets*. Não se alega "proteção de capital" como propriedade teórica da entropia (o artigo a define como regularizador estrutural, não proxy de risco).
* **Foco:** Comportamento **condicional por regime** (expansão / stress / recuperação / cauda) sob teto de variância restritivo: retorno, vol e drawdown dentro de cada bloco, não só MDD global.

---

## 6. Estrutura Esperada da Seção de Resultados

1. **Curvas de Retorno Acumulado:** Gráfico temporal comparativo por cenário de variância (permissivo/restritivo).
2. **Tabela Consolidada por regime:** Frente A no global; Frente B condicional por bloco (expansão / stress / recuperação / cauda).
3. **Discussão Prática:** Se a regularização entrópica sustenta diversificação estável fora da amostra — sem alegar superioridade sem significância nem "proteção" como propriedade teórica.
