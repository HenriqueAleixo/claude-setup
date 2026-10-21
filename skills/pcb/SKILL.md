---
name: pcb
description: Processo completo do Henrique para PCB no KiCad 10 das placas da TrueIoT/Curto, em fases — preparação, placement de cada bloco do esquemático, posicionamento dos blocos na placa, base de roteamento (netclasses, regras, malha GND, keepouts), roteamento bloco a bloco À MÃO pelo MCP, ligações entre blocos/bornes/distribuição de energia e fechamento (DRC, cantos, centro do pad, 3D, render, commit). Edição AO VIVO no pcbnew aberto só pelo MCP do KiCad. Use SEMPRE que a tarefa mexer em placa. Triggers - faz o placement, posiciona os blocos, organiza a placa, roteia o bloco, roteia a placa, faz as ligações, liga os bornes, distribui a alimentação, cria a malha GND, roda o DRC, renderiza a placa, mostra o roteamento, oculta as referências, trilha no meio do pad, /pcb.
---

# PCB KiCad (TrueIoT/Curto)

Trabalho feito **direto, na conversa** — nada de subagente. Fale em português e reporte com números (DRC, ligações
que faltam, cantos, comprimento) e com imagem.

**Como esta skill é organizada** (leia só o que a etapa pede):
- este arquivo: regras de ouro, as fases em uma linha, relato, como manter;
- `mcp.md` — pegadinhas do MCP do KiCad: **ler no começo de toda sessão de placa**;
- `fases/placement.md` (Fases 1–2) · `fases/roteamento.md` (Fases 3–5 + regras de traçado: centro do pad, ângulos,
  stackup, largura, pares, folgas) · `fases/fechamento.md` (Fase 6) — ler **antes** de começar a fase;
- `padroes/<tipo>.md` — um por tipo de bloco (hoje: `buck.md`, `canais-adc.md`) — ler antes de mexer naquele bloco.

Kit: `~/Documentos/projetos/kicad-ia-tools/pcb/` — scripts que **só leem/conferem** (tabela abaixo).
Exemplos: Ecosnap (`~/Documentos/projetos/Kicad/Ecosnap/kicad/`, roteado 10–20/10/2026), CLP ESP32
(`~/Documentos/projetos/clp-esp32/kicad/`).

## 1. Regras de ouro
1. **Toda mutação pelo MCP do KiCad** (`mcp__kicad__*` / `mcp__kicad2__*`) na placa **aberta**: mover, girar, trilha,
   via, zona, keepout, ocultar texto, salvar. Ler/analisar o arquivo salvo por script pode; mutar por kipy/pcbnew
   Python não ("porra usa mcp", 15/10; "lembra que só vamos usar mcp na pcb", 20/10). Se faltar ferramenta no MCP,
   pergunte antes.
2. **Roteamento é meu, trilha por trilha, pelo MCP.** Nada de autorouter (Freerouting) nem roteador escrito em código
   (18/10: "eu confio mais em você roteando no MCP do que no script"). Script só **confere** ou **planeja correção
   mecânica** que eu reviso (ex. `centro_pad_plano.py`). Exceção histórica: no Ecosnap, em 18/10, os blocos
   AIN/DIN/BATERIA/RELÉS foram propostos por um A* e revisados — ele aceitou manter, mas não é o processo.
3. **MCP travou** (`recovery_required`, erro repetido) → PARE, diga o que travou e peça `/mcp` → reconnect.
4. **Nunca fechar/matar o pcbnew dele nem gravar o `.kicad_pcb` por fora com ele aberto.** Ele mexe junto: releia a
   placa **ao vivo** antes de cada etapa. Título com `*` = mudança dele ainda não salva — o meu `pcb_save` grava a dele
   junto (ok, mas saiba disso).
5. **Esquemático não se edita daqui.** Problema de esquemático → item para a fila/sessão do esquemático (ver projeto).
6. **Pergunte só o que só ele sabe** (mecânica da caixa, posição travada, decisão de produto). Decisão técnica eu
   tomo, aplico e relato.
7. **Nunca apagar trilha sem repor** a ligação no mesmo lote; depois de todo lote, DRC sem violação nova e nenhuma
   rede com mais ligação faltando que antes.

## 2. Fases (uma só começa quando a anterior está fechada e mostrada a ele; dentro dela, bloco a bloco = folha)
0. **Preparação** (toda sessão): ler `mcp.md`; confirmar pelo MCP a placa certa (nome + nº de footprints, fonte
   live-gui); backup do salvo em `build/backup-*/<placa>_antes_<etapa>.kicad_pcb`; se ele mexeu, comparar ao vivo ×
   arquivo × backup e revisar só o que tem problema concreto; estado com `drc_resumo.py`.
1. **Placement de cada bloco** → `fases/placement.md`.
2. **Blocos na placa (floorplan)** → `fases/placement.md`.
3. **Base de roteamento** (netclasses, .kicad_dru, malha GND, keepouts) → `fases/roteamento.md`.
4. **Roteamento por bloco** (só ligações internas) → `fases/roteamento.md`.
5. **Ligações entre blocos, bornes, distribuição** → `fases/roteamento.md`.
6. **Fechamento** (DRC, cantos, centro do pad, refs, 3D, imagem, commit) → `fases/fechamento.md`.

## 3. Kit (`kicad-ia-tools/pcb/`, `/usr/bin/python3.12` quando importa pcbnew; tudo só lê)
| script | faz | quando |
|---|---|---|
| `drc_resumo.py placa [--area] [--novo base.json]` | DRC filtrado, violações novas, ligações faltando por rede | toda fase |
| `cantos.py placa [--area]` | curvas > 45° e 90° disfarçado | fim de cada bloco |
| `centro_pad.py placa` / `centro_pad_plano.py placa dir` | pontas fora do centro do pad / plano de correção por folha | fim de bloco, Fase 6 |
| `teste_copia.py placa lote.json [--area]` | aplica o lote numa cópia, DRC só do novo + cantos | antes de lote grande |
| `render_semgnd.py placa saida.png [--area] [--px-mm 16]` | imagem com a malha GND oculta (F vermelho, B azul, In2 laranja) | fim de cada bloco |
| `ensaio_place.py` / `satelites.py` / `opt_place.py` | ensaio de posição, satélites, otimização numa cópia | Fase 1 |
| `add3d.py placa saida` | recoloca o 3D que o move do MCP apaga (pcbnew fechado) | Fase 6 |
| `pinswap.py` | troca de GPIO (volta ao esquemático) | após Fase 2 |

## 4. Relato de cada passo
O que fiz (bloco/fase), números (trilhas, vias, DRC antes/depois, ligações que faltam), o que deixei de fora e por
quê, decisões que preciso dele — e a imagem. Antes de aplicar algo grande, diga em uma linha o que vai acontecer;
enquanto calcula fora do KiCad, avise que ainda não aplicou (ele acompanha a tela e estranha não ver mudar).

## 5. Manter esta skill viva
Toda correção dele sobre placa vira regra **na hora**, concreta e com data, **no arquivo certo**: geral/de ouro aqui;
MCP em `mcp.md`; placement, roteamento ou fechamento no arquivo da fase; jeito de fazer um tipo de bloco em
`padroes/<tipo>.md` (crie se não existir e liste no topo deste arquivo). Este arquivo fica curto (≤ ~90 linhas).
Regra que vale só para uma placa vai no README/CLAUDE.md do projeto.
