# Placement — Fases 1 e 2

## Fase 1 — Placement de cada bloco (fora da placa, se preciso)
- Bloco = folha do esquemático (`fp.GetSheetname()`). Monte o bloco **compacto e completo** antes de pensar onde ele
  fica: CI no centro, satélites em volta (tabela abaixo), cadeia de sinal em linha reta.
- Bloco novo ou muito mexido → montar numa **área livre fora do contorno** (ex. abaixo da placa), mostrar a ele, e só
  então levar para dentro. Ensaiar posições numa cópia (`ensaio_place.py`) e checar sobreposição antes do MCP.
- Folga = courtyard (sem folga extra); grid 0,25–0,5 mm; tudo no topo salvo decisão dele; referências ocultas ao fim.
- **Pense na saída do pad já no placement**: passivo ligado a um pino fica **no eixo do pino** sempre que der, para a
  trilha sair do centro de um e entrar reta no centro do outro (regra do centro do pad, `roteamento.md`). Peça fora
  do eixo obriga o desvio de 45° + 45°; se o desvio ficaria com < 0,5 mm reto antes do pad, mova a peça.
- Mostre o bloco (imagem com 3D quando ele pedir) e liste o que ficou fora do limite de satélite.

**Satélites** (passivo ligado a pino de CI fica do mesmo lado do pino, na ordem do sinal; distância pad↔pino):
desacoplamento ≤ 1,5 mm (bulk ≤ 3) · C de filtro de ADC ≤ 2 · R do RC encostado no C · cristal/C de carga, EN/reset,
divisor de FB ≤ 2–3 · R série ≤ 3 mm do pino que gera · R de gate/base ≤ 2 · pull-up/LED ≤ 5. Pad de alimentação
virado para o pino; GND para fora com via ao plano. `satelites.py` lista quem está fora.

## Fase 2 — Posicionamento dos blocos na placa (floorplan)
1. Mecânica primeiro: bornes, conectores, furos de fixação, peças **travadas pela caixa** (ex. relés do Ecosnap: "a
   posição do relê tem que ser essa que está pra não pegar na caixa") — não mova sem ele mandar.
2. Cada interface colada no seu conector: conector → proteção → condicionamento → CI.
3. Energia: proteção/bulk no borne, buck perto da entrada e de uma borda, LDO no ponto de carga.
4. Zonas sem misturar: ruidoso · analógico · digital · RF · rede/alta tensão (ilha com distância). Retorno de uma zona
   não passa sob outra.
5. Mova o bloco **inteiro** (mesmo deslocamento para todas as peças), confira sobreposição e isolação, DRC, imagem.
6. Sinal que só serve a outra placa (ex. 5G que sai pela placa de cima) não desce pelo header: o bloco vai para a placa
   onde o sinal vive.
7. Depois do floorplan, reescolher GPIO para cruzar menos (`pinswap.py`) — volta ao esquemático (fila).
