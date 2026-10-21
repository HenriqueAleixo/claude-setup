# MCP do KiCad (`kicad-mcp-pro`) — pegadinhas verificadas

Ler no começo de toda sessão de placa (Fase 0).

| ferramenta | pegadinha | o que fazer |
|---|---|---|
| `pcb_add_via` | o diâmetro é `diameter_mm`; `size_mm` é **ignorado em silêncio** e a via sai 0,8 mm | sempre `diameter_mm` + `drill_mm`; depois conte vias por tamanho |
| `pcb_set_keepout_zone` | `x_mm/y_mm` são o **centro** do retângulo, não o canto | passe o centro; confira o contorno lendo a placa |
| `pcb_add_zone` | cantos com `x_mm`/`y_mm` | — |
| `pcb_delete_items` | sempre responde "postcondition verification could not complete", mas apaga | confira lendo a placa |
| `pcb_move_footprint` | dentro de `pcb_begin_commit`/`pcb_push_commit` acusa "rotation verification failed" em peça girada, mas aplica certo; **apaga o modelo 3D** da peça movida | confira posição por leitura; no fim, `add3d.py` com o pcbnew fechado (combinar com ele) |
| `pcb_add_tracks_bulk` | camada como `F_Cu`/`B_Cu`/`In2_Cu`; rede pelo nome exato (com `·` e `/`) | lotes de ≤ 100 trilhas |
| `pcb_get_tracks` | o `id` sai **abreviado** (`7211d9dd...`) e o `pcb_delete_items` exige o UUID inteiro | pegar o UUID completo no `.kicad_pcb` salvo pelo prefixo (`grep`), depois de conferir que aberto = salvo (contagem de trilhas no `pcb_get_board_summary`) |
| várias chamadas MCP em paralelo | algumas caem em "file-backed fallback: no PCB open" e devolvem vazio | consultas de placa uma de cada vez (ou repetir a que voltou vazia) |
| `run_drc` | resposta de ~900 kB (estoura); o relatório vai para `output/drc_report.json` | comparar o json com o da base **por rede** (descrição muda com o comprimento da trilha): violação nova = 0 e nenhuma rede com mais ligação faltando |
| qualquer mudança | o preenchimento das zonas fica velho → DRC mostra dezenas de "clearance" falsos com GND | `pcb_refill_zones` + `pcb_save` antes de todo DRC |
| `pcb_place_decoupling_caps` e afins | gravam arquivo e pedem reload | não usar com a placa aberta |

- Qual MCP: `kicad` = `/tmp/kicad/api.sock` (1º KiCad). Placa num 2º KiCad → `kicad2` em `/tmp/kicad/ecosnap.sock`
  (`ln -sfn /tmp/kicad/api-<pid>.sock ...` a cada pcbnew novo). **Confira nome da placa e contagem de footprints**
  antes de editar. pcbnew aberto pelo gerenciador do KiCad roda dentro do processo `kicad` (não aparece no
  `pgrep pcbnew`): pergunte ao MCP (`pcb_get_board_summary`, fonte "live-gui").
- Abrir o pcbnew (quando ele pedir e estiver fechado): `env vblank_mode=0 setsid pcbnew placa.kicad_pcb`.
- **"KiCad is busy"**: ferramenta interativa dele ficou no meio (trilha sendo desenhada, peça no cursor). Nada
  aplicado. Perguntar a ele; com o ok: `xdotool windowactivate <janela>`, `mousemove` para o meio do canvas e
  `xdotool key Escape` duas vezes **sem `--window`** (com `--window` o wx ignora a tecla — 18/10). Conferir depois,
  comparando com o último backup, que nada dele se perdeu. Sessão Wayland: print do X sai preto, não dá para ver a tela.
- F8 (atualizar a partir do esquemático) quando ele estiver remoto: `xdotool` na janela do Eeschema/pcbnew; F8 não tira
  DNP de peça travada.
