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
- **Escolhas tomadas:** Reestruturação completa do projeto.

### 1.2. Implementação do pré-processamento

- **Data:** 10/09
- **O que:** Criação do pipeline de pré-processamento dos dados brutos de criptoativos.
- **Como:** O módulo `prep.py` executa, em ordem: (i) resample semanal `W-FRI` capturando o último preço válido da semana; (ii) *forward fill* para lacunas pontuais; (iii) *dropna* sincronizado para semanas sem cobertura de algum ativo; (iv) cálculo de retornos logarítmicos $\ln(P_t/P_{t-1})$.
- **Escolhas tomadas:**
  - **Retornos logarítmicos** em vez de simples — aditividade temporal e melhor tratamento estatístico para as estimativas de $\mu$ e covariância.
  - **Preço ajustado** (`auto_adjust=True` do yfinance) — mitiga correções fantasma de splits na API.
  - **Outliers preservados** (sem winsorização) — flash crashes são o objeto da análise de risco de cauda; limpar as quedas anularia o teste de estresse de Tsallis/Rényi.
  - **Alinhamento por sexta-feira (`W-FRI`)** como anchor semanal da amostra.
- **Observação:** O alinhamento cortou as semanas iniciais (SOL sem dados em 01/2020), iniciando a série em 04/2020 com 313 observações.

### 1.3. Implementação do modelo benchmark 1/N

- **Data:** 10/09
- **O que:** Implementação do portfólio ingênuo de pesos iguais.
- **Como:** define pesos determinísticos $w_i = 1/N$ (sem otimização), com funções para retorno do portfólio ($w^T r_t$) e retorno esperado ($w^T \mu$), lendo a série processada de retornos log.
- **Escolha tomada:** O 1/N é o **benchmark base** do estudo, conforme a narrativa do projeto — e não uma estratégia otimizada. Mantida a ordem canônica dos ativos (BTC, ETH, SOL, BNB).
- **Validado:** soma dos pesos = 1,000000; retorno esperado semanal da carteira ≈ 1,05%.

### 1.4. Implementação da otimização por entropia de Shannon

- **Data:** 10/09
- **O que:** Implementação do modelo de máxima entropia de Shannon, o primeiro modelo de otimização do arcabouço entrópico.
- **Como:** `src/modelagem/shannon.py` resolve $\max_w (-\sum w_i \ln w_i)$ sujeito a $\sum w_i = 1$, $w_i \geq 0$, $w^T\mu \geq R_{min}$.
- **Escolha tomada:** Solução via **`scipy.optimize.minimize` (SLSQP)** — versão de solver numérico genérico, mais extensível aos demais modelos (Tsallis, Rényi, KL) que nem sempre têm forma fechada. O problema é convexo (minimizar $\sum w_i \ln w_i$). Dependência `scipy` adicionada ao `requirements.txt`. Restrição inativa → retorna $1/N$; $R_{min} > \max(\mu)$ → erro de factibilidade; falha numérica → `RuntimeError`.
- **Validado:** resultados idênticos aos da solução analítica para os mesmos $R_{min}$; soma dos pesos = 1; retorno da carteira = $R_{min}$ quando a restrição é ativa.

### 1.5. Implementação da otimização por entropia de Tsallis

- **Data:** 10/09
- **O que:** Implementação do modelo de máxima entropia de Tsallis, uma generalização não-extensiva parametrizada por $q$.
- **Como:** `src/modelagem/tsallis.py` resolve $\max_w (1-\sum w_i^q)/(q-1)$ sujeito a $\sum w_i = 1$, $w_i \geq 0$, $w^T\mu \geq R_{min}$.
- **Escolha tomada:** Para $q>1$, maximizar a entropia de Tsallis equivale a minimizar $\sum w_i^q$ (o fator $1/(q-1)$ é constante) — usado como objetivo no mesmo solver `scipy.optimize.minimize` (SLSQP) de Shannon. Parâmetro $q$ configurável (padrão $q=2$, conforme o artigo); mesmo protocolo de factibilidade (restrição inativa → uniforme; $R_{min} > \max(\mu)$ → erro).
- **Validado:** $q \to 1$ recupera a solução de Shannon; com $q$ maior, os pesos concentram-se menos em SOL e redistribuem para BNB/ETH (penalização mais forte de concentração); $H_q$ decrescente em $q$.

### 1.6. Implementação da otimização por entropia de Rényi

- **Data:** 10/09
- **O que:** Implementação do modelo de máxima entropia de Rényi, generalização parametrizada por $\alpha$ com foco em sensibilidade ao risco de cauda.
- **Como:** `src/modelagem/renyi.py` resolve $\max_w \frac{1}{1-\alpha}\ln(\sum w_i^\alpha)$ sujeito a $\sum w_i = 1$, $w_i \geq 0$, $w^T\mu \geq R_{min}$, minimizando diretamente $-H_\alpha$ no mesmo solver SLSQP.
- **Escolha tomada:** $\alpha$ configurável (padrão $\alpha=2$); para $\alpha \to 1$ recupera-se Shannon. Mesma convenção de factibilidade dos demais modelos.
- **Validado:** $\alpha \to 1$ → mesma solução de Shannon (H_α ≈ ln 4); $\alpha$ maior concentra menos em SOL e redistribui para BNB (penalização de concentração equivalente à de Tsallis, como previsto pela teoria).

### 1.7. Implementação da otimização por entropia ponderada de Shannon (WSE)

- **Data:** 10/09
- **O que:** Implementação do modelo de entropia de Shannon ponderada, que incorpora pesos informacionais $u_i > 0$ por ativo.
- **Como:** `src/modelagem/wse.py` resolve $\max_w (-\sum u_i w_i \ln w_i)$ sujeito a $\sum w_i = 1$, $w_i \geq 0$, $w^T\mu \geq R_{min}$, minimizando $\sum u_i w_i \ln w_i$ via SLSQP.
- **Escolha tomada:** Com $u_i = 1$ para todos, recupera-se Shannon; $u$ permite refletir prioridades informacionais (ex.: market cap, liquidez). $u$ default = uniforme, mas testado com $u$ favorecendo BTC/ETH.
- **Validado:** com $u = [3,2,1,1]$ (BTC/ETH favorecidos), as alocações com restrição ativa privilegiam esses ativos — a ponderação altera o padrão de diversificação conforme esperado.

### 1.8. Implementação da otimização por divergência de Kullback-Leibler

- **Data:** 10/09
- **O que:** Implementação do modelo de controle estrutural via divergência de Kullback-Leibler.
- **Como:** `src/modelagem/kl.py` resolve $\min_w \sum w_i \ln(w_i/p_i)$ sujeito a $\sum w_i = 1$, $w_i \geq 0$, $w^T\mu \geq R_{min}$, mantendo a carteira próxima de uma referência $p_i$ (default $1/N$), via SLSQP.
- **Escolha tomada:** $p$ default = $1/N$ (benchmark ingênuo), mas aceita referências arbitrárias (ex.: market-cap-like); com $p = 1/N$, KL = 0 quando a restrição é inativa.
- **Validado:** KL mínimo com pesos iguais na restrição inativa; com restrição ativa, a carteira desvia-se da referência o mínimo necessário para atingir $R_{min}$.

### 1.9. Implementação do backtest walk-forward com janela móvel

- **Data:** 10/09/2026
- **O que:** Arquitetura de avaliação fora da amostra: backtest *walk-forward* com janela de estimação móvel e rebalanceamento semanal, cobrindo todos os modelos (1/N, Shannon, Tsallis, Rényi, WSE, KL).
- **Como:** `src/modelagem/backtest.py` executa, em cada semana de corte $t$:
  1. **Recorte da janela de treinamento** — últimas $J=52$ semanas ($t-52$ a $t-1$);
  2. **Estimação** do vetor de retorno esperado $\mu = \overline{r}_{\text{janela}}$ por ativo;
  3. **Resolução do otimizador** de cada modelo sujeito a $\sum w = 1$, $w \geq 0$, $w^T\mu \geq \rho$;
  4. **Execução out-of-sample** — pesos fixos $w^*$ aplicados ao retorno da semana $t$, descontado o custo de transação $c \cdot \sum_i |\Delta w_i|$;
  5. **Avanço rolling** — descarta a semana mais antiga, incorpora a mais recente e repete.
- **Escolhas tomadas:**
  - **Janela de estimação $J = 52$ semanas** — horizonte anual, lento o bastante para estimativa estável de $\mu$, rápido o bastante para acompanhar regimes do mercado cripto.
  - **Rebalanceamento semanal** com custo proporcional a $|\Delta w|$ — o custo desestimula o *turnover* excessivo, tornando a comparação realista entre modelos.
  - **Segurança numérica (SLSQP):** durante testes, o `x0 = uniforme` causava falha de linha de busca ("Positive directional derivative") em 1 das 260 janelas (2022-05-20, bear market), quando a restrição ativa força concentração. A correção foi um **warm-start** ($x_0$ concentrado no ativo de maior $\mu$ quando a restrição é ativa, e uniforme quando inativa), centralizado na função `ponto_inicial` de `ingenuo.py` e usado por todos os otimizadores — validado com 0 falhas em todas as 260 janelas.
  - **Meta de retorno $\rho$:** parâmetro fixo semanal ($\rho = 1\%$). Quando $\rho$ é atingido pela carteira uniforme, a restrição é inativa e o modelo retorna $1/N$ (solução MaxEnt irrestrita). Quando $\rho > \max(\mu)$ (infactível, 42% das janelas — períodos de baixa), o modelo retorna à carteira uniforme: decisão metodológica de **não forçar "intuitivamente" a concentração** no menos-pior ativo, pois isso transformaria a restrição sombra do artigo em uma regra de *chasing*, violando o princípio MaxEnt.
  - **Avaliação:** retorno acumulado e anualizado (Frente A), vol anual, Sharpe, Sortino e Max Drawdown (Frente B).
- **Validação:** 260 semanas de teste (2021-04-16 a 2026-04-03); soma dos pesos = 1 em todas as janelas (erro máx. $10^{-13}$); restrição ativa em 12% das semanas (32 das 260), infactível em 42% (fallback uniforme); quando ativa, Shannon diverge até ~0.13 de Tsallis/Rényi, enquanto WSE (com $u=1$) e KL (com $p=1/N$) coincidem com Shannon — consistente com a teoria.
- **Evidência:** resultados salvos em `resultados/` (`retornos-backtest.csv`, `curvas-acumuladas.csv`, `tabela-metricas.csv`).

### 1.10. Implementação do módulo de visualização de resultados

- **Data:** 11/09
- **O que:** Módulo de visualização gráfica dos resultados do backtest, voltado à leitura exploratória e à seleção de figuras para o artigo.
- **Como:** `src/visualizacao/viz.py` lê os CSVs persistidos em `resultados/` e gera cinco famílias de figuras em `resultados/graficos/`:
  1. **curvas-acumuladas.png** — riqueza relativa em escala log, comparando os modelos ao longo do tempo;
  2. **drawdown.png** — drawdown em relação ao pico acumulado (Frente B);
  3. **retornos-semanais.png** — série de retornos líquidos out-of-sample;
  4. **metricas.png** — barras comparativas das métricas da tabela (acumulado, anualizado, vol, Sharpe, Sortino, MDD);
  5. **pesos.png** — painel de áreas empilhadas com a evolução temporal dos pesos de cada modelo (recomputa os pesos via `backtest()`).
- **Escolhas tomadas:**
  - **Paleta fixa por modelo** (cor consistente em todas as figuras) e **escala log** nas curvas acumuladas — em crescimento composto, a escala linear achata a leitura inicial; a log suaviza a diferença de magnitude entre períodos.
  - **Padrão Chart-like de figuras**: grade leve, sem spines superior/direito, legenda em três colunas, `tight_layout` com `bbox_inches="tight"` para produção direta de figuras para a redação.
  - **Reuso dos CSVs** em vez de recomputar o backtest em cada execução (apenas os pesos são recomputados, pois não são persistidos).
- **Validado:** as 5 figuras são geradas sem erro; cores de todos os modelos detectáveis em `curvas-acumuladas.png` (dados realmente plotados); sobreposição de Shannon/WSE/KL e proximidade de Tsallis/Rényi na escala log refletem os ~12% de semanas com restrição ativa.
- **Evidência:** `resultados/graficos/*.png` (5 arquivos).

### 1.11. Auditoria da metodologia e dos resultados (diagnóstico)

- **Data:** 11/09
- **O que:** Revisão crítica de toda a cadeia metodológica (dados → modelos → backtest → métricas → visualização), cruzando o desenho empírico com o artigo de referência e validando numericamente os artefatos gerados.
- **Principais achados (do mais ao menos grave):**
  1. **Restrição de retorno ativa em apenas 12% das semanas.** Com $\rho = 1\%$ semanal fixo: (i) em ~46% das janelas a carteira uniforme já atinge $\rho$ → os modelos retornam `1/N`; (ii) em ~42% $\rho > \max(\mu)$ (infactível, períodos de baixa) → fallback para `1/N`; (iii) só ~12% têm restrição ativa e factível. Nos períodos mais estressados (exatamente onde a Frente B deveria diferenciar o arcabouço), todos os modelos colapsam no benchmark. **Causa raiz: o alvo fixo de 1% semanal não é factível em bear markets.** O artigo de referência evita isso deliberadamente: o alvo é **escolhido para ser factível e vinculante em todos os regimes** (seção 2.5 e Apêndice C.1), algo que o projeto não replicou.
  2. **Redundância de modelos: 6 "modelos" = 3 problemas.** Com os defaults escolhidos, Tsallis $q=2$ e Rényi $\alpha=2$ reduzem-se ao mesmo problema ($\min \sum w_i^2$) — diferença numérica < $5\times10^{-7}$; WSE com $u_i=1$ e KL com $p=1/N$ são idênticos a Shannon ($\min \sum w_i\ln w_i$). O backtest confirma: shannon ≡ wse ≡ kl (dif. $\approx 10^{-7}$) e tsallis ≡ renyi. O WSE só diverge com $u \neq 1$ e o KL só com $p \neq 1/N$ — mas o projeto usou os defaults neutros. O artigo usa $u = (0.35,0.30,0.20,0.15)$ (ponderado por market cap/liquidez) e $q=2$ apenas para Tsallis (não testa Rényi como "inovação").
  3. **Retorno logarítmico linearizado no período de teste.** O backtest combina retornos logaritmicos por $w^T r_t^{log}$ e acumula $\prod (1+w^T r^{log})$. Isso subestima geometricamente o crescimento (o gap de convexidade média semanal ≈ 0,62 p.p.: média $w \cdot r^{simpl} = 0,74\%$ vs. $w \cdot r^{log} = 0,11\%$). Recomputado com retornos **simples**, o 1/N acumula +145% no período de teste vs. −54% reportado. **As métricas da tabela estão enviesadas para baixo e não representam a performance real.**
  4. **Divergência da especificação do artigo (sem restrição de variância).** O artigo otimiza sob retorno mínimo **e** limite superior de variância (restrição (iv) nas seções 2.5 e Apêndice A). O projeto omitiu a restrição de variância — a carteira resultante tem vol anual ~64%, i.e., o arcabouço entrópico aqui não controla risco de forma explícita, apenas concentração.
  5. **Backtest cobre 2021–2026, não "janela histórica 2020–2025 + avaliação 2026"** como consta na seção 4 do registro — o desenho real (walk-forward desde a primeira janela) é defensável, porém diverge do plano documentado.
- **Conclusão:** a arquitetura (janela móvel, custos de transação, warm-start e fallback MaxEnt) está correta e estável; mas o **conjunto de escolhas de parâmetros** (alvo fixo, defaults neutros, retornos log linearizados, ausência de restrição de variância) torna os resultados atuais **não representativos** da comparação proposta pelo artigo e **numericamente enviesados**.

### 1.12. Correção dos cinco problemas da auditoria

- **Data:** 11/09
- **O que:** Implementação das cinco correções apontadas na auditoria (1.11), realinhando a cadeia metodológica com o artigo de referência e validando os resultados em retornos simples.
- **Como, por inversão de severidade:**
  1. **Retornos simples em todo o backtest.** `prep.py` passou a gerar `dados/prep/retornos-simples-semanais.csv` (coleção de `retornos_simples()`); `backtest.py` estima $\mu$, covariância, executa e acumula tudo em retornos aritméticos (`ARQUIVO_RETORNOS` apontando para o CSV de simples). O 1/N que reportava −54% passou a **+145,4%** (riqueza 2,454) no período de teste — consistente com a validação da auditoria. `viz.py` também passou a ler os retornos simples (inclusive para recomputar os pesos).
  2. **Defaults não-neutros.** Para eliminar a redundância de modelos: Rényi com $\alpha = 3.0$ (não mais 2, que o reduzia ao Tsallis); WSE com $u = (0.35, 0.30, 0.20, 0.15)$ (market cap/liquidez, conforme o artigo); KL com $p = (0.50, 0.25, 0.15, 0.10)$ (dominância de BTC). Cada modelo ganhou uma `carteira_base()` própria (retorno MaxEnt irrestrita): 1/N para Shannon/Tsallis/Rényi e a referência $u$/$p$ para WSE/KL — o fallback de infactibilidade deixou de ser sempre 1/N.
  3. **Meta de retorno $\rho$ dinâmica e factível.** `meta_retorno()` define $\rho = \max(rf_{semanal},\ \mu^T w_{1/N} + f_{meta}(\max\mu - \mu^T w_{1/N}))$ com $f_{meta}=0.5$ e $rf=0$: alvo entre o retorno do benchmark e o melhor ativo da janela → **sempre factível**, vinculante quando há dispersão e adaptado ao regime (acompanha o mercado em bear). Nas 260 janelas, $\rho$ foi vinculante em 100% delas.
  4. **Restrição de variância $w^T\Sigma w \le \sigma^2_{max}$.** Adicionada arquivada como em 1.11.2: `sigma2_max = f_{var} \cdot w_{1/N}^T \Sigma w_{1/N}` (variância do benchmark na janela), calibrada em `fator_var = 2.0`. Calibração: `fator_var=1.0` deixa ~2/3 das janelas infactíveis (colapso em base); `fator_var=3.0` nunca ativa a restrição; `fator_var=2.0` mantém ~80% das janelas com otimização ativa e a variância como guardrail ativo em ~6% das semanas. `ingenuo.py` ganhou `restricoes_padrao()` (soma, retorno e variância) reutilizada por todos os modelos, e `ponto_inicial()` agora aceita covariância/$\sigma^2_{max}$ para warm-start ciente da variância (interpolação uniforme↔concentrado por bissecção quando o uniforme viola o teto).
  5. **Narrativa temporal alinhada ao desenho real.** A seção 4 passou a descrever corretamente o walk-forward: **warm-up 2020–2021 (janela inicial de 52 semanas) + backtest out-of-sample 2021–2026** (260 semanas).
- **Depuração notável:** o primeiro run com covariância falhou com erro do SLSQP (“Input array gradx must be 1D”), causado por chamadas posicionais erradas em `_resolver` (o 3º argumento de Tsallis/Rényi/WSE/KL é $q/\alpha/u/p$, não covariância) — corrigido passando `cov=` e `sigma2_max=` como argumentos nomeados.
- **Validado:** backtest roda sem fallback em 33 das 260 janelas; todos os modelos diferenciam-se do 1/N (riqueza final: 1/N 2,454 < shannon 2,629 < tsallis 2,609 < renyi 2,632 < wse 2,739 < kl 3,079); restrição de retorno ativa em 100% das janelas, de variância em ~6%; métricas em `resultados/tabela-metricas.csv` e figuras regeneradas em `resultados/graficos/`.
- **Evidência:** `resultados/*.csv` e `resultados/graficos/*.png` regenerados (11/09).

---

## 2. Contexto e Motivação

Segundo Dedu & Șerban (2026), a otimização tradicional de portfólios
(Markowitz, média-variância) falha em criptoativos devido à alta volatilidade,
assimetria e distribuições de retornos com caudas pesadas.

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

| Item                  | Definição                                                     |
| --------------------- | --------------------------------------------------------------- |
| Ativos                | BTC, ETH, SOL, BNB                                              |
| Fonte                 | yfinance (`dados.py`)                                         |
| Frequência           | semanal                                                         |
| Warm-up (estimação)  | 2020–2021 (janela inicial de 52 semanas semanal retroativa)     |
| Backtest out-of-sample | 2021-04-16 a 2026-04-03 (260 semanas, walk-forward)            |
| Arquivos              |  `dados/precos-semanais.csv`, `dados/prep/retornos-simples-semanais.csv` |

---

## 5. Modelos a Implementar

Detalhamento completo em `notas/modelos.md`. Resumo das restrições comuns:

$$
\sum_i w_i = 1, \quad w_i \geq 0, \quad w^T\mu \geq \rho, \quad w^T\Sigma w \leq \sigma^2_{max}
$$

com $\rho = \max(rf_{sem}, \mu^T w_{1/N} + f_{meta}(\max\mu - \mu^T w_{1/N}))$ (dinâmico, $f_{meta}=0.5$)
e $\sigma^2_{max} = f_{var} \cdot w_{1/N}^T \Sigma w_{1/N}$ ($f_{var}=2.0$).

| Modelo            | Objetivo                                                   | Default não-neutro                    |
| ----------------- | ---------------------------------------------------------- | -------------------------------------- |
| $1/N$           | Benchmark ingênuo                                         | —                                      |
| Shannon           | $\max -\sum w_i \ln w_i$                                 | —                                      |
| Tsallis ($q=2$) | $\max \frac{-\sum w_i^q}{q-1}$                           | —                                      |
| Rényi            | $\max \frac{1}{1-\alpha}\ln\left(\sum w_i^\alpha\right)$ | $\alpha = 3.0$                         |
| WSE              | $\max -\sum u_i w_i \ln w_i$                             | $u = (0.35,0.30,0.20,0.15)$            |
| Kullback-Leibler  | $\min \sum w_i \ln(w_i/p_i)$                             | $p = (0.50,0.25,0.15,0.10)$            |

---

## 6. Checklist de Implementação

- [X] Aquisição e pré-processamento dos dados (Retornos simples semanais; warm-up 2020–2021, teste 2021–2026).
- [X] Implementação das funções objetivo (1/N, Shannon, Tsallis, Rényi, KL, WSE) com restrições de retorno e variância.
- [X] Arquitetura do backtest com janela móvel e rebalanceamento periódico.
- [X] Cálculo das métricas de desempenho (Frente A, Frente B e eficiência geral).
- [X] Correção dos cinco problemas da auditoria (1.12) e regeneração de resultados/figuras.
- [ ] Analise dos resultados obtidos.
- [ ] Redação do artigo.
