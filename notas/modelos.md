
# Modelos de Otimização a serem Trabalhados no Projeto

Todas as restrições comuns traduzem o problema fundamental de alocação de portfólio sob as premissas do projeto:

* **Orçamento:** A soma dos pesos investidos não pode exceder 1 (100% do capital).
  $$
  \sum_i^N w_i = 1
  $$
* **Positividade:** Não são permitidas posições vendidas ( *short selling* ); os pesos devem ser não-negativos.
  $$
  w_i \geq 0
  $$
* **Retorno Mínimo:** A alocação deve atingir ou superar um patamar de retorno esperado pré-estabelecido.
  $$
  w^T\mu \geq R_{min}
  $$

### 1. 1/N — Benchmark Base

* **Descrição:** Alocação ingênua com pesos iguais em todos os ativos. Serve como o piso informacional e de custo-benefício do mercado.

  $$
  w_i = \frac{1}{N}
  $$

  *(Obs.: Não envolve otimização matemática direta).*

### 2. Shannon Entropy (Baseline do Artigo)

* **Descrição:** Maximiza a incerteza informacional clássica, forçando uma distribuição de pesos mais homogênea e livre de pressupostos paramétricos rígidos.

  $$
  \max_w \left( -\sum_i w_i \ln(w_i) \right)
  $$

  **Sujeito a:**

  $$
  w^T\mu \geq R_{min}, \quad \sum_i w_i = 1, \quad w_i \geq 0
  $$

### 3. Tsallis Entropy (Baseline do Artigo)

* **Descrição:** Generalização não-extensiva controlada pelo parâmetro **$q$**, altamente sensível e adaptada para lidar com distribuições de caudas pesadas ( *fat-tails* ), típicas de criptoativos.

  $$
  \max_w \left( \frac{-\sum_i w_i^q}{q - 1} \right)
  $$

  **Sujeito a:**

  $$
  w^T\mu \geq R_{min}, \quad \sum_i w_i = 1, \quad w_i \geq 0
  $$

### 4. Rényi Entropy (Inovação / Foco em Risco de Cauda)

* **Descrição:** Generalização informacional parametrizada por **$\alpha$**. Permite modular a sensibilidade do modelo para focar na mitigação de perdas extremas ou na captura de ganho.

  $$
  \max_w \left( \frac{1}{1 - \alpha} \ln \left( \sum_i w_i^\alpha \right) \right)
  $$

  **Sujeito a:**

  $$
  w^T\mu \geq R_{min}, \quad \sum_i w_i = 1, \quad w_i \geq 0
  $$

### 5. Kullback-Leibler Divergence / Entropia Relativa (Inovação / Controle Estrutural)

* **Descrição:** Minimiza a distância informacional entre os pesos resultantes da otimização e uma distribuição de referência prévia (**$p_i$**, como o próprio **$1/N$** ou  *Market Cap* ), impedindo alocações extremas ou "alucinações" do otimizador.

  $$
  \min_w \left( \sum_i w_i \ln\left(\frac{w_i}{p_i}\right) \right)
  $$

  **Sujeito a:**

  $$
  w^T\mu \geq R_{min}, \quad \sum_i w_i = 1, \quad w_i \geq 0
  $$
