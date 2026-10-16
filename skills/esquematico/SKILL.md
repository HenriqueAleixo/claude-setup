---
name: esquematico
description: Procedimento e regras do Henrique para esquemático no KiCad 10 das placas da TrueIoT/Curto (ESP32, IoT, CLP, medidores, drivers) — esquemático hierárquico gerado por script, uma folha por módulo, peças só das libs pessoais (LCSC/JLCPCB, Basic primeiro, 0402), estilo visual dele, revisão de pinagem contra datasheet, escolha/importação de peça, ERC e PDF. Use SEMPRE que a tarefa mexer em esquemático ou BOM de placa. Triggers - monta o esquemático, cria a folha de, troca essa peça, revisa o esquemático, confere a pinagem, passa pra 0402, gera o PDF do esquemático, escolhe a peça, importa da LCSC, define os GPIOs, /esquematico.
---

# Esquemático KiCad (TrueIoT/Curto)

Trabalho feito **direto, na conversa** — nada de subagente. Fale em português, direto, e justifique decisão de
circuito com números (corrente, tensão, potência, limite do datasheet).

Kit: `~/Documentos/projetos/kicad-ia-tools/` (leia o `README.md`: `schlib.py`/`draw.py`, `lcsc/busca.py`,
`lcsc/importa.py`, `lcsc/libscan.py`). Exemplo completo: CLP ESP32 em `~/Documentos/projetos/clp-esp32/kicad/`
(`gen_sch.py` + `sh_*.py` + README).

## 1. Antes de mexer
- Projeto novo vai em `~/Documentos/projetos/<nome>/kicad/` (nunca na home). `git init`, commit por folha.
- **Eeschema FECHADO sem salvar** (`pgrep -a eeschema`). Se estiver aberto, peça para ele fechar *sem salvar* e
  espere. Nunca mate o processo. Motivo: o Eeschema guarda a versão velha em memória; em 29/09 o F8 usou ela e o
  "salvar tudo" sobrescreveu a pinagem nova do ESP32 do medidor.
- Se ele mexeu à mão no esquemático, pergunte o que foi e traga para o script antes de regenerar (regenerar apaga
  edição manual).
- Decisões de projeto (faixa de tensão, tipo de entrada/saída, nº de canais, bornes, conectores) são dele:
  pergunte antes de assumir. O resto (valores, peças, topologia de proteção) você decide e registra.

## 2. Como gerar
- O esquemático é **gerado por script** (`gen_sch.py` + um `sh_<bloco>.py` por folha). O KiCad 10 não tem API
  de esquemático ao vivo.
- Ferramentas `sch_*` do MCP têm defeitos (path de instância errado em folha filha, "~" nos pinos, sem
  LCSC/Description): use o MCP só para **revisar** — `run_erc`, `sch_trace_net`, `sch_get_connectivity_graph`, BOM.
- Depois de gerar: `kicad-cli sch erc` (zero erro; aviso de tipo de pino das LCSC é aceitável), PDF em
  `output/esquematico.pdf`, render das folhas mexidas (`pdftoppm`) e **olhe a imagem** antes de dizer que está
  pronto. Compare a netlist com a versão anterior sempre que mexer em layout de folha. Commit.
- Pendência de datasheet fica `[CONFIRMAR]` no README até ser verificada.
- Estudos para artigo (BreakoutC3, MedidorEnergia, ControladorVentilador): pipeline por script + `docs/LOG.md`
  com o prompt dele verbatim, tempo e custo, commit por iteração.

## 3. Estrutura
- Hierárquico: uma folha por módulo funcional; referências por centena por folha (FONTE 1xx, DI 2xx…).
- Placas empilhadas no mesmo projeto: folhas por placa + folha de interligação, pinagem idêntica dos dois lados.
- Folhas **compactas** (A4/A3, sem terço vazio). "Mais espaço" é dentro do bloco, não entre blocos. Bloco com
  título curto; a conta vai numa nota de cálculo (linhas ≤ ~75 caracteres).

## 4. Estilo visual (obrigatório)
- Textos 30 mil, referência em **negrito**; número/nome de pino só em CI, transistor, MOSFET, opto, relé e
  conector; valor do resistor dentro do corpo; posições padronizadas (o `draw.py` já faz).
- **Passivo sempre ligado por fio** ao nó a que pertence (RC, divisor, pull-up, gate, série, realimentação,
  bootstrap). Nada de peça solta ligada por label — "parece netlist". Label só entre CIs distantes ou entre folhas.
- Desacoplamento em grupo, pendurado num trilho curto com o símbolo de alimentação. PWR_FLAG nas saídas de regulador.
- Símbolo da LCSC que obriga a cruzar fio → símbolo de projeto com a mesma numeração (`custom_syms`).
- Canais repetidos com passo folgado (ex. entradas digitais: 25,4 mm entre canais).

## 5. Peças
- Só das libs pessoais (`~/.local/share/kicad/10.0/3rdparty/kicad-libs`: LCSC, JLCPCB-*); nunca `Device:*` nem
  símbolo convertido do EasyEDA. Amp-op/lógica podem usar o desenho da lib padrão com footprint/LCSC das libs dele.
- JLC: **Basic**, depois Preferred. **Nunca trocar Basic por Extended** — nem por aviso de montagem difícil (a
  revisão da JLC custa ~o mesmo que o setup da Extended). Trocas válidas: Extended → Basic/Preferred.
- Faltou peça: `lcsc/busca.py` (estoque/tipo) e `lcsc/importa.py C…` (vai para a lib LCSC global, sem commit no
  repo kicad-libs — avise). Sem equivalente → o Basic mais próximo, listado no README/LOG.
- Tamanho **0402** por padrão (lógica, desacoplamento 3,3/5 V, pull-ups, série). 0603+ quando: rede de 24 V ou
  campo (o 100 nF 0402 Basic é 16 V), dissipação > ~50 mW, borne de campo (surto), chassi/blindagem.
- **Pinagem conferida no datasheet** antes de fechar (URL da LCSC:
  `https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/<arquivo>.pdf`). Ex.: o HR911105A tinha LEDs invertidos e o
  CHS GND ia para o chassi — o datasheet manda.

## 6. Regras de circuito já definidas
- ESP32-S3: strapping 0/3/45/46 (45/46 só com sinal que tem pull-down — gate de MOSFET, LED, enable com 100 k);
  IO35–37 proibidos no N16R8 (PSRAM octal); USB 19/20; UART0 43/44 para gravação; SPI rápido nos pinos IO_MUX
  (SPI2 = IO10–13). Depois do placement, reescolher GPIO para cruzar menos (`pcb/pinswap.py`) e trazer a troca
  para o script do esquemático.
- Conector exposto (expansão, campo): alimentação nos cantos, cercada de GND; ESD (SRV05-4) nos sinais, depois
  do resistor série (33 Ω SPI, 100 Ω CS/INT); alimentação externa por chave limitada (TPS2553) + PTC.
- Bornes no padrão CLP: em cima, da esquerda, L+ M, entradas, analógicas, alimentação de sensores; embaixo as
  saídas, com posições vazias isolando contato de relé (rede) das saídas 24 V.
- Entrada 12–30 V: PTC + diodo série + TVS; relé com bobina 5 V do buck (aciona em toda a faixa).
- Regulador perto de quem consome (o LDO 3,3 V foi para a placa do S3, que liga só com USB).

## 7. Ao terminar
Relate o que mudou, números do ERC, pendências `[CONFIRMAR]` e o commit, e mostre a imagem das folhas mexidas.

## 8. Manter esta skill viva
Toda correção dele sobre esquemático ("não quero assim", "isso sempre…") vira regra **nesta** SKILL.md, na seção
certa, concreta e verificável, com a data — na mesma hora, sem esperar o fim da tarefa. Regra que vale só para
uma placa vai no CLAUDE.md/README do projeto, não aqui.
