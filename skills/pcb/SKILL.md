---
name: pcb
description: Processo completo do Henrique para PCB no KiCad 10 das placas da TrueIoT/Curto, em fases — preparação, placement de cada bloco do esquemático, posicionamento dos blocos na placa, base de roteamento (netclasses, regras, malha GND, keepouts), roteamento bloco a bloco À MÃO pelo MCP, ligações entre blocos/bornes/distribuição de energia e fechamento (DRC, cantos, 3D, render, commit). Edição AO VIVO no pcbnew aberto só pelo MCP do KiCad. Use SEMPRE que a tarefa mexer em placa. Triggers - faz o placement, posiciona os blocos, organiza a placa, roteia o bloco, roteia a placa, faz as ligações, liga os bornes, distribui a alimentação, cria a malha GND, roda o DRC, renderiza a placa, mostra o roteamento, oculta as referências, /pcb.
---

# PCB KiCad (TrueIoT/Curto)

Trabalho feito **direto, na conversa** — nada de subagente. Fale em português e reporte com números (DRC, ligações
que faltam, cantos, comprimento) e com imagem.

O processo tem 7 fases (seção 3). **Uma fase só começa quando a anterior está fechada e mostrada a ele.** Dentro de
cada fase o trabalho é bloco a bloco (bloco = folha do esquemático).

Kit: `~/Documentos/projetos/kicad-ia-tools/pcb/` — scripts que **só leem/conferem** (tabela na seção 5).
Exemplos: Ecosnap (`~/Documentos/projetos/Kicad/Ecosnap/kicad/`, roteado 10–18/10/2026), CLP ESP32
(`~/Documentos/projetos/clp-esp32/kicad/`).

## 1. Regras de ouro
1. **Toda mutação pelo MCP do KiCad** (`mcp__kicad__*` / `mcp__kicad2__*`) na placa **aberta**: mover, girar, trilha,
   via, zona, keepout, ocultar texto, salvar. Ler/analisar por script pode; mutar por kipy/pcbnew Python não ("porra
   usa mcp", 15/10). Se faltar ferramenta no MCP, pergunte antes.
2. **Roteamento é meu, trilha por trilha, pelo MCP.** Nada de autorouter (Freerouting) nem roteador escrito em código
   (18/10: "eu confio mais em você roteando no MCP do que no script"). Script só **confere** (DRC, cantos, imagem,
   teste numa cópia). Exceção histórica: no Ecosnap, em 18/10, os blocos AIN/DIN/BATERIA/RELÉS foram propostos por um
   A* e revisados — ele aceitou manter, mas não é o processo.
3. **MCP travou** (`recovery_required`, erro repetido) → PARE, diga o que travou e peça `/mcp` → reconnect.
4. **Nunca fechar/matar o pcbnew dele nem gravar o `.kicad_pcb` por fora com ele aberto.** Ele mexe junto: releia a
   placa **ao vivo** (`pcb_get_footprints`, fonte "live-gui") antes de cada etapa. Título com `*` = mudança dele ainda
   não salva — o meu `pcb_save` grava a dele junto (ok, mas saiba disso).
5. **Esquemático não se edita daqui.** Problema de esquemático → item para a fila/sessão do esquemático (ver projeto).
6. **Pergunte só o que só ele sabe** (mecânica da caixa, posição travada, decisão de produto). Decisão técnica eu
   tomo, aplico e relato.

## 2. Pegadinhas do MCP `kicad-mcp-pro` (verificadas)
| ferramenta | pegadinha | o que fazer |
|---|---|---|
| `pcb_add_via` | o diâmetro é `diameter_mm`; `size_mm` é **ignorado em silêncio** e a via sai 0,8 mm | sempre `diameter_mm` + `drill_mm`; depois conte vias por tamanho |
| `pcb_set_keepout_zone` | `x_mm/y_mm` são o **centro** do retângulo, não o canto | passe o centro; confira o contorno lendo a placa |
| `pcb_add_zone` | cantos com `x_mm`/`y_mm` | — |
| `pcb_delete_items` | sempre responde "postcondition verification could not complete", mas apaga | confira lendo a placa |
| `pcb_move_footprint` | dentro de `pcb_begin_commit`/`pcb_push_commit` acusa "rotation verification failed" em peça girada, mas aplica certo; **apaga o modelo 3D** da peça movida | confira posição por leitura; no fim, `add3d.py` com o pcbnew fechado (combinar com ele) |
| `pcb_add_tracks_bulk` | camada como `F_Cu`/`B_Cu`/`In2_Cu`; rede pelo nome exato (com `·` e `/`) | lotes de ≤ 100 trilhas |
| qualquer mudança | o preenchimento das zonas fica velho → DRC mostra dezenas de "clearance" falsos com GND | `pcb_refill_zones` + `pcb_save` antes de todo DRC |
| `pcb_place_decoupling_caps` e afins | gravam arquivo e pedem reload | não usar com a placa aberta |
- Qual MCP: `kicad` = `/tmp/kicad/api.sock` (1º pcbnew). Placa num 2º KiCad → `kicad2` em `/tmp/kicad/ecosnap.sock`
  (`ln -sfn /tmp/kicad/api-<pid>.sock ...` a cada pcbnew novo). **Confira nome da placa e contagem de footprints**
  antes de editar.
- Abrir o pcbnew (quando ele pedir e estiver fechado): `env vblank_mode=0 setsid pcbnew placa.kicad_pcb`.
- **"KiCad is busy"**: ferramenta interativa dele ficou no meio (trilha sendo desenhada, peça no cursor). Nada
  aplicado. Perguntar a ele; com o ok: `xdotool windowactivate <janela>`, `mousemove` para o meio do canvas e
  `xdotool key Escape` duas vezes **sem `--window`** (com `--window` o wx ignora a tecla — 18/10). Conferir depois,
  comparando com o último backup, que nada dele se perdeu. Sessão Wayland: print do X sai preto, não dá para ver a tela.
- F8 (atualizar a partir do esquemático) quando ele estiver remoto: `xdotool` na janela do Eeschema/pcbnew; F8 não tira
  DNP de peça travada.

## 3. Processo em fases

### Fase 0 — Preparação (toda sessão)
1. `pgrep -a pcbnew`; confirmar que o MCP enxerga a placa certa (nome + nº de footprints).
2. Backup do arquivo salvo em `build/backup-*/<placa>_antes_<etapa>.kicad_pcb` antes de cada fase.
3. Se ele disse que mexeu: comparar **ao vivo × arquivo × último backup** (posição/rotação/camada por ref) e listar o
   que mudou antes de opinar. Revisar a mudança dele com DRC daquela área e devolver só o que tem problema concreto.
4. Saber o estado: `drc_resumo.py` (violações + ligações que faltam por rede).

### Fase 1 — Placement de cada bloco (fora da placa, se preciso)
- Bloco = folha do esquemático (`fp.GetSheetname()`). Monte o bloco **compacto e completo** antes de pensar onde ele
  fica: CI no centro, satélites em volta (tabela da seção 4), cadeia de sinal em linha reta.
- Bloco novo ou muito mexido → montar numa **área livre fora do contorno** (ex. abaixo da placa), mostrar a ele, e só
  então levar para dentro. Ensaiar posições numa cópia (`ensaio_place.py`) e checar sobreposição antes do MCP.
- Folga = courtyard (sem folga extra); grid 0,25–0,5 mm; tudo no topo salvo decisão dele; referências ocultas ao fim.
- Mostre o bloco (imagem com 3D quando ele pedir) e liste o que ficou fora do limite de satélite.

### Fase 2 — Posicionamento dos blocos na placa (floorplan)
1. Mecânica primeiro: bornes, conectores, furos de fixação, peças **travadas pela caixa** (ex. relés do Ecosnap: "a
   posição do relê tem que ser essa que está pra não pegar na caixa") — não mova sem ele mandar.
2. Cada interface colada no seu conector: conector → proteção → condicionamento → CI.
3. Energia: proteção/bulk no borne, buck perto da entrada e de uma borda, LDO no ponto de carga.
4. Zonas sem misturar: ruidoso · analógico · digital · RF · rede/alta tensão (ilha com distância). Retorno de uma zona
   não passa sob outra.
5. Mova o bloco **inteiro** (mesmo deslocamento para todas as peças), confira sobreposição e isolação, DRC, imagem.
6. Sinal que só serve a outra placa (ex. 5G que sai pela placa de cima) não desce pelo header: o bloco vai para a placa
   onde o sinal vive.

### Fase 3 — Base de roteamento (antes da primeira trilha)
1. **Netclasses** no `.kicad_pro` por padrão de nome (`netclass_patterns`): Default 0,2 · PWR_LOW 0,4 · PWR 0,8 ·
   PWR_IN 1,0 · REDE_AC 2,5 (5 A) · ISO 0,3 — ajustar à corrente (tabela IPC na seção 4).
2. **Regras custom** no `.kicad_dru`: AC × baixa tensão 3 mm, AC × AC 1,5 mm, ISO × zona não isolada 4 mm; exceção por
   footprint para CI de passo fino. Sintaxe: `A.NetClass == 'X'`, `B.Type == 'Zone'`, `A.memberOfFootprint('R1')`;
   `B.NetName != 'unconnected-*'` (não existe `!startsWith` nem curinga em referência).
3. **Malha GND: uma zona por rede de terra configurada nas 4 camadas** (F/In1/In2/B), não uma zona por camada. Ilha
   isolada (ex. GNDB do RS485) = zona própria com prioridade maior, nas 4 camadas, costurada por vias.
4. **Keepouts** (sem polígono) onde não pode GND em camada nenhuma: área dos contatos de relé, sob RJ45 com magnético,
   antena. Confira o contorno depois (centro × canto).
5. Polígonos de potência só onde precisa: nós do buck (VIN/SW/GND/VOUT) em F.Cu, prioridade alta, sólidos.
6. Mostre a imagem da base (zonas) antes de rotear.

### Fase 4 — Roteamento por bloco (só ligações internas)
- Escopo: ligação em que **as duas pontas são peças da mesma folha**. Borne, header e alimentação que vem de outro
  bloco ficam para a Fase 5 ("é só roteia os blocos por enquanto, depois vamos fazer a ligação entre eles").
- Ordem dentro do bloco: laço de potência/desacoplamento → cristal/clock → pares diferenciais → sinais analógicos →
  digitais → pull-ups/LEDs → costura de GND (via ao plano em todo pad de GND, a ≤ 1–2 mm do pad).
- Desenho: coordenadas pensadas por mim a partir dos pads reais (ler pads/obstáculos da área por script), em JSON;
  testar o lote com `teste_copia.py` (DRC só do que é novo + cantos); só então `pcb_add_tracks_bulk` + `pcb_add_via`.
- **Barramento** (vários sinais paralelos, ex. expansor → 4 drivers): planejar as faixas antes; se a ordem dos pinos
  é inversa à dos destinos, o sinal que sai por baixo cruza por B.Cu com um par de vias. Leque a 45° com `x+y`
  constante para manter o espaçamento.
- Fino passo (MSOP/TSSOP 0,5–0,65): saída pelo eixo do pad, curva só depois de sair da fileira.
- **Canais repetidos chegando num CI** (entradas de ADC, saídas de expansor): nada de serpentear entre as peças do
  bloco na F.Cu (18/10, ADS1115: "não estou gostando como as trilhas chegam… não tem como vir pela bot?"). Cada canal
  desce por via junto do seu filtro/proteção, corre em **faixa reta na B.Cu** paralela às outras e sobe por via colada
  no pino. Se a ordem física dos canais não casa com a ordem dos pinos e as entradas são equivalentes, propor **troca
  de pinos** (vai para a fila do esquemático + F8; avisar o contrato de firmware) em vez de cruzar faixas.
- **Rede de alimentação vai na In2 também dentro do bloco** (18/10: "+15VA … teria que estar no In2 não?"): toda rede
  das classes PWR_IN/PWR/PWR_LOW (trilho de regulador, 3V3, +15VA…) corre na In2; em F/B só o toco pad → via e o
  desacoplamento colado no pino. Classe de rede define largura/folga/via, **não a camada** — a camada é minha.
- **Polígono × trilha na In2** (18/10: "4 pontas já tem que entrar como polígono"): rede de alimentação com **≥ 4
  pontas** (pads/vias que ela alimenta no bloco) = **polígono na In2**, prioridade acima da malha GND, cobrindo só a
  região das pontas; < 4 pontas = trilha larga na In2. **Exceção: alimentação analógica de baixa corrente** (ex.
  3V3A do ADC, < 1 mA) vai como trilha fina na In2 mesmo com muitas pontas, para a In2 continuar GND sob o bloco
  analógico e as faixas da B.Cu terem referência limpa (18/10, AIN do Ecosnap). Cada pad desce por toco curto + via até o polígono. Duas redes
  de alimentação disputando a mesma área da In2: uma vira polígono e a outra contorna; se não der, cruza por um trecho
  curto em B.Cu (registrar).
- Depois de cada polígono: `pcb_refill_zones` e conferir **ilhas = 1** (`GetFilledPolysList(...).OutlineCount()`).
  Faixa estreita é cortada por vias de outras redes (18/10: dedo de 1,4 mm do +5V partido por GND/OD/B−): levar a
  faixa por onde não há via, com ≥ 1 mm livre depois das folgas.
- Pente de pull-ups colado no CI (passo < 1 mm, sem vaga para via por pad) fica em F.Cu como leque curto; só a
  alimentação do pente desce para o polígono por uma via na ponta.
- **Todo pad de GND precisa da sua via** (o polígono de F.Cu não chega entre trilhas finas). Pad cercado → desviar
  ~0,5 mm a trilha vizinha para abrir a vaga (18/10, D411 do AIN); nunca via dentro do pad SMD.
- Fechou o bloco: `pcb_refill_zones` → `pcb_save` → `drc_resumo.py --area` (0 violação nova) → `cantos.py --area`
  (0) → `render_semgnd.py` da área → mandar a imagem e relatar.

### Fase 5 — Ligações entre blocos, bornes e distribuição
1. Sinais entre blocos: rotas curtas, sem passar por dentro de outro bloco; respeitar zonas (analógico × ruidoso).
2. Bornes: contatos AC largos em F+B (5 A → ≥ 2,8 mm externa), dentro do keepout, com as folgas AC; sinais de campo
   pela cadeia de proteção.
3. **Alimentação na In2 como trilha larga** (ex. VIN_5G_RAW 1 mm); **polígono só quando a rede ramifica muito**
   ("só faz polígono quando tiver muita ramificação"). Vias de potência 0,8/0,4, várias em paralelo (≤ 1 A por via).
4. Header entre placas: conferir pino a pino com a outra placa.
5. Ao fim: 0 ligações faltando na placa (`drc_resumo.py`).

### Fase 6 — Fechamento
1. `pcb_refill_zones`, DRC 0 erro (ruído aceito: lib_footprint_mismatch, silk, starved_thermal de borne TH —
   relatar o número).
2. `cantos.py` sem curva > 45° e sem segmento < 0,5 mm entre duas curvas.
3. Referências ocultas (0 visíveis); peças novas sem DNP indevido.
4. Modelos 3D: contar `(model ` no arquivo; se caiu, com o pcbnew fechado (combinado com ele): `add3d.py`.
5. Imagem final (malha oculta + 3D se ele pedir), `pcb_save`, commit do projeto com o que mudou.

## 4. Regras técnicas
**Satélites** (passivo ligado a pino de CI fica do mesmo lado do pino, na ordem do sinal; distância pad↔pino):
desacoplamento ≤ 1,5 mm (bulk ≤ 3) · C de filtro de ADC ≤ 2 · R do RC encostado no C · cristal/C de carga, EN/reset,
divisor de FB ≤ 2–3 · R série ≤ 3 mm do pino que gera · R de gate/base ≤ 2 · pull-up/LED ≤ 5. Pad de alimentação
virado para o pino; GND para fora com via ao plano. `satelites.py` lista quem está fora.

**Buck**: laço quente mínimo (Cin no VIN, diodo/chave no SW, GND dos dois no mesmo ponto), indutor fora do laço, nada
sensível sob indutor/SW, FB longe do SW, nós em polígono F.Cu.

**Ângulos**: só 0/45/90; **nenhum canto de 90°** e nenhum "90° disfarçado" (duas curvas de 45° coladas) — entre duas
curvas, ≥ 0,5 mm reto. Curva dentro do pad não conta.

**Stackup 4 camadas**: F sinal · In1 GND contínuo · In2 alimentação em trilhas largas (polígono só com muita
ramificação) + GND no resto · B sinal. GND nas 4 camadas. Não cruzar sinal sobre divisão de plano; via de GND a
≤ 5 mm de cada via de sinal que troca de camada.

**Largura** (IPC-2152, 1 oz, ΔT 10 °C, externa): 0,5 A 0,12 · 1 A 0,3 · 2 A 0,8 · 3 A 1,4 · 4 A 2,0 · 5 A 2,8 mm;
interna ≈ 2,6× e JLC 4L interna é 0,5 oz. Via 0,3/0,6 ≤ 1 A. JLC: sinal 0,2/0,2, alimentação ≥ 0,4, cobre↔borda
≥ 0,5 (regra do projeto). ESP32: alimentação ≥ 25 mil.

**Pares**: USB 90 Ω ≈ 0,21/0,13 · Ethernet 100 Ω ≈ 0,17/0,15 (JLC04161H-7628), sem via, sem stub, curtos.

**Folga por tensão** (fontes em `REGRAS_ROTEAMENTO.md`): IPC-2221C (230 Vac = 325 Vpk: externa c/ máscara 1,6 mm);
IEC 60664-1: contato↔contato de relé ≥ 1,5 mm no ar / 2,5 mm superfície; rede ↔ SELV reforçada ≥ 6 mm em todas as
camadas; rasgo só conta com ≥ 1 mm de largura. Isolação funcional de RS485 isolado: 4 mm (decisão dele, Ecosnap).
**Jumper/0 Ω entre redes AC** (ex. seletor de snubber NA/NF): footprint com pads ≥ 1,5 mm de folga (1206 ou maior) —
0402 deixa 0,44 mm e trava o roteamento.

## 5. Kit (`kicad-ia-tools/pcb/`, rodar com `/usr/bin/python3.12` quando importa pcbnew)
| script | faz | quando |
|---|---|---|
| `drc_resumo.py placa [--area] [--novo base.json]` | DRC filtrado, violações novas, ligações faltando por rede | toda fase |
| `cantos.py placa [--area]` | curvas > 45° e 90° disfarçado | fim de cada bloco |
| `teste_copia.py placa lote.json [--area]` | aplica o lote numa cópia, DRC só do novo + cantos | antes de cada lote no MCP |
| `render_semgnd.py placa saida.png [--area]` | imagem com a malha GND oculta (F vermelho, B azul, In2 laranja) | fim de cada bloco |
| `ensaio_place.py` / `satelites.py` / `opt_place.py` | ensaio de posição, satélites, otimização numa cópia | Fase 1 |
| `add3d.py placa saida` | recoloca o 3D que o move do MCP apaga (pcbnew fechado) | Fase 6 |
| `pinswap.py` | troca de GPIO (volta ao esquemático) | após Fase 2 |

## 6. Relato de cada passo
O que fiz (bloco/fase), números (trilhas, vias, DRC antes/depois, ligações que faltam), o que deixei de fora e por
quê, decisões que preciso dele — e a imagem. Antes de aplicar algo grande, diga em uma linha o que vai acontecer;
enquanto calcula fora do KiCad, avise que ainda não aplicou (ele acompanha a tela e estranha não ver mudar).

## 7. Manter esta skill viva
Toda correção dele sobre placa vira regra **nesta** SKILL.md, na seção certa, concreta e com data — na mesma hora.
Regra que vale só para uma placa vai no README/CLAUDE.md do projeto.
