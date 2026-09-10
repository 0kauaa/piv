
# Proposta de Projeto de Artigo: Otimização de Portfólio em Criptomoedas via Teoria da Informação

---

## 1. Contextualização e Diagnóstico

A otimização tradicional de portfólios baseada no modelo de **Markowitz (Média-Variância)** falha flagrantemente no mercado de criptoativos. Devido à alta volatilidade, assimetria (*skewness*) e distribuições de retornos com caudas pesadas (*fat-tailed*), as premissas paramétricas do Markowitz desmoronam, gerando erros severos de estimação e portfólios hiperconcentrados.

Seguindo a premissa de Silvia Dedu e Florentin Șerban (*Entropy-Based Portfolio Optimization in Cryptocurrency Markets*), este projeto adota a **Entropia** como um regulador estrutural e livre de premissas rígidas (*distribution-free*), garantindo uma diversificação geométrica natural por meio da Teoria da Informação.

---

## 2. A Narrativa do Projeto

Diferente do artigo original — que foca fortemente na derivação matemática do arcabouço unificado de Máxima Entropia (MaxEnt) comparando Shannon, Tsallis e Weighted Shannon —, este projeto adota uma **abordagem pragmática e empírica**.

O foco não é reescrever a teoria, mas sim **colocar diferentes formulações entrópicas à prova frente aos dados reais de criptomoedas**, utilizando o clássico portfólio ingênuo **$1/N$ (pesos iguais) como benchmark base**. A narrativa do artigo gira em torno da utilidade prática: *qual método de entropia realmente entrega o melhor desempenho sob o caos do mercado cripto?*

---

## 3. Metodologia e Escopo de Comparação

O projeto compara o desempenho histórico (*backtest*) das seguintes estratégias na mesma base de dados de criptoativos:

* **Benchmark Base:** Portfólio Ingênuo ($1/N$).
* **Arcabouço Entrópico:**
* Entropia de Shannon
* Entropia de Tsallis
* Entropia Ponderada de Shannon (*Weighted Shannon*)
* Entropia de Rényi
* Entropia de Kullback-Leibler

---

## 4. O Coração Analítico: "Ganho" vs. "Perda"

Para fugir de análises superficiais de rentabilidade, o estudo divide a avaliação dos resultados em duas frentes complementares:

### Frente A: Agressividade e Captura de Ganho (Upside)

* **Objetivo:** Avaliar qual formulação de entropia consegue surfar melhor as altas explosivas (*bull markets*) inerentes ao mercado cripto.
* **Foco:** Retorno acumulado total e Retorno Anualizado.

### Frente B: Resiliência e Proteção de Capital (Downside)

* **Objetivo:** Responder à premissa de que **otimizar o ganho não é a mesma coisa que minimizar a perda**. Em cripto, evitar o fundo do poço importa mais do que acertar o topo.
* **Foco:** Comportamento do portfólio em ciclos de baixa (*bear markets*), profundidade de quedas máximas (*Max Drawdown*) e eficiência ajustada ao risco de cauda.

---

## 5. Estrutura Esperada da Seção de Resultados

1. **Curvas de Retorno Acumulado:** Gráfico temporal comparativo evidenciando o crescimento do capital de cada estratégia.
2. **Tabela Consolidada de Desempenho:** Confronto direto entre ganho (retorno) e proteção (drawdown/volatilidade de baixa).
3. **Discussão Prática:** Conclusões diretas sobre qual entropia equilibra melhor a expansão de capital e a sobrevivência em ambientes de alto estresse financeiro.
