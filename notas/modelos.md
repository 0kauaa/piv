# modelos de otimização a serem trabalhados no projeto

todas as restrições são iguais entre os modelos, pois traduzem o problema de otimização de portifóloio:

- **orçamento:** a ideia é minimizar a perda dado um orçamento fixo, portanto, a soma dos pesos (quanto será investido em cada uma das carteiras) não pode ser maior que 1.

$$
\sum_i^N{w_u} = 1
$$

- **positividade:** não é possível investivir valores negativos em nehuma das carteiras.

$$
w_i \geq 0
$$

- **retorno mínimo:** a minimização de perda deve encontrar uma distribuição de pesos que esteja de acordo com retorno esperado mínimo.

$$
w^T\mu \geq R_{min}
$$


1. **1/N - benchmark base**

$$
\frac{1}{N}
$$

obs.: não há maximização nem minimização aqui.

1. **Markowitz - Média-Variância**

$$
min_w(w^T\sum{w})
$$

sujeito a:

$$
w^T\mu \geq R_{min} \\
\sum_i w_i = 1 \\
w_i \geq 0
$$

1. **Shannon Entropy**

$$
max_w(-\sum{w_i} \mathrm{ln}(w_i))
$$

sujeito a:

$$
w^T\mu \geq R_{min} \\
\sum_i w_i = 1 \\
w_i \geq 0
$$

1. **Tsallis Entropy**

$$
max_w(\frac{-\sum_i{w_i^q}}{q - 1})
$$

sujeito a:

$$
w^T\mu \geq R_{min} \\
\sum_i w_i = 1 \\
w_i \geq 0
$$

1. **Weighted Shannon Entropy**

$$
max_w(-\sum_i{u_i w_i \mathrm{ln}(w_i)})
$$

sujeito a:

$$
w^T\mu \geq R_{min} \\
\sum_i w_i = 1 \\
w_i \geq 0
$$
