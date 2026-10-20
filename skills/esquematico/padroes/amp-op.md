# Padrão de desenho: amp-op (com ou sem estágio de saída)

Referências: LT AN18 fig. 1a/2 (estágio de potência dentro da malha), TI SLOS068 fig. 8-1 (LM358).
Primeiro uso: Ecosnap AOUT, 20/10/2026 (`scripts/sh_i_aout.py`, `channel()`).

- Triângulo da lib padrão (`Amplifier_Operational`), uma unidade por canal, dentro do bloco do canal; a unidade
  de alimentação fica no bloco do CI/fonte com o desacoplamento no pino (`decap_pin`). Footprint/LCSC da JLC no Part.
- **− em cima** (espelhar em x), + embaixo. Entrada chega no + pela esquerda.
- **Realimentação por cima** do canal inteiro: do ponto onde é tomada (saída ou borne) volta numa linha horizontal
  acima de tudo e desce no nó −. Nunca por baixo (cruza o estágio de saída e a proteção).
- C de compensação logo acima do amp-op, entre o nó − e a saída.
- R do nó − para o GND pendurado na linha do nó −, à esquerda do amp-op; se a entrada do + ficar no caminho do GND,
  a entrada desce uma linha.
- Estágio de saída (seguidor) à direita, na altura da saída; limitação de corrente (BC847 + R sensor) colada no
  seguidor, transistor espelhado com a base virada para o R sensor.
- Proteção/carga/leitura de volta numa linha horizontal à direita, com os shunts pendurados (GND alinhados).
- Ligações entre peças com `connect()` (draw.py); label só para o que sai do bloco (DACn, AOUTn, AOUTn_RB).
