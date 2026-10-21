# Padrão de placa: canais repetidos chegando num CI (ADC, expansor)

Origem: 18/10, ADS1115 do Ecosnap — "não estou gostando como as trilhas chegam… não tem como vir pela bot?".

- Nada de serpentear entre as peças do bloco na F.Cu.
- Cada canal desce por via junto do seu filtro/proteção, corre em **faixa reta na B.Cu** paralela às outras e sobe
  por via colada no pino.
- Se a ordem física dos canais não casa com a ordem dos pinos e as entradas são equivalentes, propor **troca de
  pinos** (vai para a fila do esquemático + F8; avisar o contrato de firmware) em vez de cruzar faixas.
- Alimentação analógica de baixa corrente (3V3A) como trilha fina na In2, para a In2 seguir GND sob o bloco.
