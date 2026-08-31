# possíveis modelos

1. seleção + alocação + rebalanceamento

$max(w^T \mu - \lambda w^T \sum w)$

2. seleção + alocação + rebalanceamento + entropia (sugestão do professor)

$max(w^T \mu - \lambda w^T \sum w + \gamma H(w)) \mid H(w) = -\sum_{i=1}^N w_i \mathrm{ln}(w_i) $

dedu et al. (2026) propoẽ uma otimização de portifólio baseado no princípio da máxima entropia. a diversificação da carteira pode ser tratada como um problema de informação/incerteza, e não somente como um problema de variância.
