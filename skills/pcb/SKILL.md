---
name: pcb
description: Procedimento e regras do Henrique para PCB no KiCad 10 das placas da TrueIoT/Curto — edição AO VIVO no pcbnew aberto só pelo MCP do KiCad (kicad/kicad2), floorplan, placement por bloco do esquemático, passivos satélites, buck/cristal/Ethernet/USB/antena do ESP32, 4 camadas, roteamento trilha a trilha a 45° sem canto de 90°, folga por tensão/isolação, DRC e render. Use SEMPRE que a tarefa mexer em placa. Triggers - faz o placement, organiza a placa, otimiza o placement, arruma o laço do buck, posiciona a ethernet, roteia a placa, cria os planos, roda o DRC, renderiza a placa, troca os pinos do ESP32, oculta as referências, /pcb.
---

# PCB KiCad (TrueIoT/Curto)

Trabalho feito **direto, na conversa** — nada de subagente. Fale em português e reporte com números
(cruzamentos, comprimento, área de laço, DRC).

Kit: `~/Documentos/projetos/kicad-ia-tools/pcb/` (README, `opt_place.py`, `pinswap.py`, `REGRAS_ROTEAMENTO.md`).
Exemplo: CLP ESP32 em `~/Documentos/projetos/clp-esp32/kicad/`.

## 1. Regra nº 1 — ao vivo, só pelo MCP, nunca por cima dele
- **Toda mutação** (mover, girar, virar de lado, trilha, via, zona, ocultar texto, salvar) vai pelas ferramentas
  do MCP do KiCad (`mcp__kicad__*` / `mcp__kicad2__*`) na placa **aberta**. Ler/analisar por script pode; mutar
  por kipy/pcbnew Python não ("porra usa mcp", 15/10). Se faltar ferramenta no MCP para algo, pergunte antes.
- **MCP travou** (`recovery_required`, "postcondition failed", erro repetido) → PARE, diga o que travou e peça
  `/mcp` → reconnect. Não continue por kipy "para não esperar".
- Qual MCP: `kicad` usa `/tmp/kicad/api.sock` (1º pcbnew aberto). Placa num 2º KiCad → `kicad2`, que lê
  `/tmp/kicad/ecosnap.sock`; a cada pcbnew novo refazer `ln -sfn /tmp/kicad/api-<pid>.sock /tmp/kicad/ecosnap.sock`
  (pid em `pgrep -a pcbnew`). **Antes de editar, confira o nome da placa e a contagem de footprints** — o socket
  pode estar em outra placa.
- **Nunca matar/fechar o pcbnew dele e nunca gravar o `.kicad_pcb` por fora com o editor aberto** (inclui
  ferramentas do MCP que gravam arquivo e pedem reload, ex. `pcb_place_decoupling_caps`). "KiCad is busy" = ele
  está editando: espere ou pergunte. (03/10: matar o pcbnew apagou mudanças dele.)
- Ele mexe junto: **releia a placa ao vivo** antes de cada etapa. Antes de mudança em bloco, peça Ctrl+S; depois
  salve (`pcb_save`) e faça commit. O `.history/` do projeto guarda saves e autosaves.
- Pegadinhas do `pcb_move_footprint`: dentro de `pcb_begin_commit`/`pcb_push_commit` acusa "rotation verification
  failed" em toda peça que gira, mas o push aplica certo (confira lendo a placa); fora de transação, um
  "postcondition failed" deixa o servidor em `recovery_required`.
- Nunca apague/recrie footprint pela API (kipy `update_items` apaga o 3D — se acontecer, pedir Ferramentas →
  Atualizar footprints a partir da biblioteca).
- Exceções: estudos para artigo (BreakoutC3, MedidorEnergia, ControladorVentilador) seguem pipeline por script +
  `docs/LOG.md`; mala-ensaio-rele ele pediu sem abrir o KiCad → pcbnew headless, só com a placa fechada.
  Scripts que geram a placa do zero (`place_pcb.py`) só quando não existe placa; depois ficam congelados.

## 2. Ritmo de trabalho
- **Bloco a bloco** (= folha do esquemático): aplicar pelo MCP → conferir (sobreposição, courtyard, isolação,
  refs ocultas) → DRC → imagem → relatar o bloco. Decisão técnica eu tomo e registro (README/LOG); só paro se o
  MCP travar ou faltar informação que só ele tem (ex. datasheet da caixa).
- **Referências ocultas**: ao fim de cada etapa de placement e a cada F8 que trouxer peça nova, ocultar os textos
  de referência e conferir 0 visíveis.

## 3. Floorplan — antes do placement fino
1. Mecânica e conectores primeiro (bornes, USB, RJ45, antena, fixação, caixa) — definem as bordas.
2. Cada interface colada no seu conector, na ordem do sinal: conector → proteção (TVS/ESD/PTC) → condicionamento → CI.
3. Energia segue entrada → conversão → carga: proteção e bulk no borne; **buck perto da entrada e de uma borda**,
   longe de analógico/cristal/antena; **LDO no ponto de carga**; desacoplamento no pino; bulk na entrada de cada bloco.
4. Zonas sem misturar: ruidoso (buck, relé, indutivo) · analógico (entre o conector e o ADC; ADC na fronteira com o
   digital) · digital · RF · rede/alta tensão (ilha com distância/rasgo). Retorno de uma zona não passa sob outra.
5. Ordem: cristal, desacoplamento, laço do buck, pares diferenciais, antena — depois o resto.
6. Calor espalhado (regulador, bobina de relé, resistor de potência), com cobre, longe de cristal e sensor.
7. No fim, encolher o contorno ao necessário (mantendo bordas presas por mecânica/conector e alinhamento de
   headers de placas empilhadas).

## 4. Placement
- **Cada peça perto do seu bloco do esquemático** (mesma folha). Nunca mandar peça para a região de outro bloco só
  porque reduz cruzamento (15/10: o bulk da fonte foi parar na frente dos bornes DI). Agrupe por sheetpath do
  netlist, restrinja a busca à região do bloco e liste peças fora do bloco.
- Formato da família quando houver (ex. Medidor: 80 × 86,5 mm, bornes DB128V-5.0-15P nas bordas).
- Conectores, bornes, USB, RJ45, botões nas bordas; antena do ESP32 na borda (ou para fora), sem cobre embaixo em
  nenhuma camada e ~15 mm livre em volta.
- Placas empilhadas: header da de cima espelhado embaixo; **confira pino a pino** com a de baixo (já esteve 180°).
- Folga = **limite do courtyard** (sem folga extra), protegendo os pads (footprint importado às vezes tem courtyard
  só no corpo — `opt_place.py` usa courtyard ∪ pads + 0,1 mm). Grid 0,5 mm.
- Otimização: `opt_place.py` numa cópia (FIXED = o que ele posicionou; DECAP_W alto; COMPACT ~1; BEAUTY=1), aplicar
  o resultado **pelo MCP**, DRC, relatar antes/depois.
- Desacoplamento: pad de **alimentação virado para o pino**, GND para fora com via ao plano; o menor capacitor mais
  perto. (Exceção: capacitor de saída de buck — GND junto do diodo.)
- Buck: laço quente mínimo — Cin colado no VIN, diodo/chave colado no SW, GND do Cin e do diodo no mesmo ponto;
  indutor fora do laço; nada sensível sob o indutor ou o nó SW; meça o laço pelos pads (a crítica do MCP
  superestima). Nó de DC-DC sempre com polígonos.
- Cristal colado nos pinos (≤ ~2 mm), capacitores de carga logo atrás, sem trilha embaixo.
- **Passivos satélites** (04/10): passivo ligado a um pino de CI fica **do mesmo lado do CI que o pino**, na ordem do
  sinal. Distância pad↔pino:
  | satélite | máx. |
  |---|---|
  | desacoplamento (um por pino de alimentação) | ≤ 1,5 mm (bulk do bloco ≤ 3 mm) |
  | C de filtro de entrada de ADC/comparador | ≤ 2 mm |
  | R do filtro RC | encostado no C (≤ 1,5 mm), do lado de fora |
  | cristal + C de carga, R/C de reset/EN, divisor de FB | ≤ 2–3 mm |
  | R série de SPI/clock/UART | ≤ 3 mm do pino que **gera** o sinal |
  | R de gate/base | ≤ 2 mm |
  | pull-up/pull-down, R de LED | ≤ 5 mm |
  Cadeias (borne → proteção → divisor → R → C → pino) em linha reta, na altura do pino. Antes de fechar, liste os
  satélites fora do limite e corrija.
- Ethernet (WIZnet + TI/ADI): W5500 a < 25 mm do RJ45, cadeia reta RJ45 → terminações → série 33 Ω → CI; nenhum
  plano sob RJ45 com magnético (restrição nas camadas internas e de baixo); pares 100 Ω, curtos, sem via.
- Depois do placement, troca de GPIO (`pinswap.py`) — a mudança volta para o esquemático (skill `esquematico`).

## 5. Roteamento
- **Eu decido cada trilha e desenho pelo MCP** (`pcb_add_tracks_bulk` / `pcb_add_via`), bloco a bloco, DRC + imagem a
  cada bloco. Nada de autorouter (Freerouting) nem roteador escrito em código.
- Ângulos só 0/45/90 e **nenhum canto de 90°**: toda mudança de direção chanfrada a 45°. Confira os cantos antes de
  passar ao próximo bloco (`pcb_route_corner_style_gate`).
- Stackup 4 camadas: F.Cu sinal · In1 **GND contínuo** (sem cortes) · In2 alimentação **só em polígonos locais por
  rede**, nunca um plano cobrindo a placa · B.Cu sinal. No fim, **GND em todas as camadas** (preencher F.Cu e B.Cu).
- Não cruzar sinal sobre divisão de plano; via de GND a ≤ 5 mm de cada via de sinal que troca de camada; costura
  ≤ λ/20 (≈ 3 mm p/ 2,4 GHz; ≤ 5 mm na borda e em volta de RF/Ethernet); via do capacitor a ≤ 1–2 mm do pino.
- Largura (IPC-2152, 1 oz, ΔT 10 °C), externa: 0,5 A 0,12 · 1 A 0,3 · 2 A 0,8 · 3 A 1,4 · 4 A 2,0 · 5 A 2,8 mm;
  interna ≈ 2,6× e as internas da JLC 4L são 0,5 oz → corrente fica nas externas. Via 0,3/0,6: ≤ 1 A por via.
  ESP32: alimentação principal ≥ 25 mil, VDD3P3 ≥ 20 mil, demais 10 mil; 10 µF antes do módulo.
- JLC 4L: mínimo 0,09/0,09, mas trabalhe com sinal 0,2/0,2, alimentação ≥ 0,4, via 0,3/0,6, anel ≥ 0,2, cobre ↔
  borda ≥ 0,2 (≥ 0,3 em fresado).
- Pares (JLC04161H-7628, L1 sobre L2 — conferir na calculadora JLC e pedir impedância controlada): USB 90 Ω ≈
  0,21/0,13 mm, desvio ≤ 1,27 mm; Ethernet 100 Ω ≈ 0,17/0,15 mm, ≥ 20 mil entre TX e RX, MDI < 25 mm. Paralelos,
  sem via, sem stub; 5W entre pares rápidos, 3W entre sinais comuns; teardrop em pad/via ↔ trilha fina.
- Laço do buck e retornos de potência largos e curtos; FB longe do SW/indutor.

## 6. Folga por tensão e isolação (fontes em `kicad-ia-tools/pcb/REGRAS_ROTEAMENTO.md`)
- IPC-2221C Tab. 6-1 (mm):
  | V pico | interna | externa s/ máscara | externa c/ máscara |
  |---|---|---|---|
  | ≤ 30 | 0,05 | 0,10 | 0,075 |
  | 31–100 | 0,10 | 0,64 | 0,30 |
  | 101–300 | 0,20 | 1,25 | 0,80 |
  | 301–500 (230 Vac = 325 Vpk) | 0,25 | 2,50 | 1,60 |
- IEC 60664-1 / 62368-1 (230 V, poluição 2, FR-4 IIIb) — vale o maior: contato↔contato do relé e rede↔PE: ar
  ≥ 1,5 (CAT II) / 3,0 mm (CAT III), superfície ≥ 2,5 mm; **rede ↔ SELV = reforçada → regra da casa ≥ 6,0 mm em
  todas as camadas**, nenhum plano interno atravessa a barreira.
- Rasgo só reduz a distância de superfície se tiver ≥ 1,0 mm de largura; não muda a distância no ar.
- CLP (IEC 61131-2): I/O 24 V SELV ↔ lógica ≥ 0,5 mm; TVS + R série colados no borne, retorno do TVS curto ao
  terra de proteção sem passar pela lógica, filtro depois da proteção.

## 7. Ao terminar
DRC zero erro (folga de furo interna de footprint de biblioteca é aceitável), render 3D/imagem do bloco, `pcb_save`,
commit. Relate o que mudou, métricas antes/depois, DRC e commit, com a imagem.

## 8. Manter esta skill viva
Toda correção dele sobre placa ("tem trilha com noventa graus", "lembra de ocultar") vira regra **nesta** SKILL.md,
na seção certa, concreta e verificável, com a data — na mesma hora. Regra que vale só para uma placa vai no
CLAUDE.md/README do projeto, não aqui.
