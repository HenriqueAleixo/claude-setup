# Roteamento — Fases 3, 4 e 5 (+ regras técnicas de traçado)

## Fase 3 — Base de roteamento (antes da primeira trilha)
1. **Netclasses** no `.kicad_pro` por padrão de nome (`netclass_patterns`): Default 0,2 · PWR_LOW 0,4 · PWR 0,8 ·
   PWR_IN 1,0 · REDE_AC 2,5 (5 A) · ISO 0,3 — ajustar à corrente (tabela de largura abaixo). O padrão casa pelo
   **nome da rede**: rede renomeada no esquemático perde a classe no F8 (20/10, B− do Ecosnap).
2. **Regras custom** no `.kicad_dru`: AC × baixa tensão 3 mm, AC × AC 1,5 mm, ISO × zona não isolada 4 mm; exceção por
   footprint para CI de passo fino. Sintaxe: `A.NetClass == 'X'`, `B.Type == 'Zone'`, `A.memberOfFootprint('R1')`;
   `B.NetName != 'unconnected-*'` (não existe `!startsWith` nem curinga em referência).
3. **Malha GND: uma zona por rede de terra configurada nas 4 camadas** (F/In1/In2/B), não uma zona por camada. Ilha
   isolada (ex. GNDB do RS485) = zona própria com prioridade maior, nas 4 camadas, costurada por vias.
4. **Keepouts** (sem polígono) onde não pode GND em camada nenhuma: área dos contatos de relé, sob RJ45 com magnético,
   antena. Confira o contorno depois (centro × canto).
5. Polígonos de potência só onde precisa: nós do buck (VIN/SW/GND/VOUT) em F.Cu, prioridade alta, sólidos.
6. Mostre a imagem da base (zonas) antes de rotear.

## Fase 4 — Roteamento por bloco (só ligações internas)
- Escopo: ligação em que **as duas pontas são peças da mesma folha**. Borne, header e alimentação que vem de outro
  bloco ficam para a Fase 5 ("é só roteia os blocos por enquanto, depois vamos fazer a ligação entre eles").
- Ordem dentro do bloco: laço de potência/desacoplamento → cristal/clock → pares diferenciais → sinais analógicos →
  digitais → pull-ups/LEDs → costura de GND (via ao plano em todo pad de GND, a ≤ 1–2 mm do pad).
- Desenho: coordenadas pensadas por mim a partir dos pads reais (centro do pad, ver abaixo), em JSON; aplicar com
  `pcb_add_tracks_bulk` + `pcb_add_via` e conferir com o DRC do MCP comparado com a base.
- **Barramento** (vários sinais paralelos, ex. expansor → 4 drivers): planejar as faixas antes; se a ordem dos pinos
  é inversa à dos destinos, o sinal que sai por baixo cruza por B.Cu com um par de vias. Leque a 45° com `x+y`
  constante para manter o espaçamento.
- Fino passo (MSOP/TSSOP 0,5–0,65): saída pelo eixo do pad, curva só depois de sair da fileira.
- **Canais repetidos chegando num CI**: ver `padroes/canais-adc.md`.
- **Rede de alimentação vai na In2 também dentro do bloco** (18/10: "+15VA … teria que estar no In2 não?"): toda rede
  das classes PWR_IN/PWR/PWR_LOW (trilho de regulador, 3V3, +15VA…) corre na In2; em F/B só o toco pad → via e o
  desacoplamento colado no pino. Classe de rede define largura/folga/via, **não a camada** — a camada é minha.
- **Polígono × trilha na In2** (18/10: "4 pontas já tem que entrar como polígono"): rede de alimentação com **≥ 4
  pontas** (pads/vias que ela alimenta no bloco) = **polígono na In2**, prioridade acima da malha GND, cobrindo só a
  região das pontas; < 4 pontas = trilha larga na In2. **Exceção: alimentação analógica de baixa corrente** (ex.
  3V3A do ADC, < 1 mA) vai como trilha fina na In2 mesmo com muitas pontas, para a In2 continuar GND sob o bloco
  analógico e as faixas da B.Cu terem referência limpa (18/10, AIN do Ecosnap). Cada pad desce por toco curto + via
  até o polígono. Duas redes de alimentação disputando a mesma área da In2: uma vira polígono e a outra contorna; se
  não der, cruza por um trecho curto em B.Cu (registrar).
- Depois de cada polígono: `pcb_refill_zones` e conferir **ilhas = 1**. Faixa estreita é cortada por vias de outras
  redes (18/10: dedo de 1,4 mm do +5V partido por GND/OD/B−): levar a faixa por onde não há via, com ≥ 1 mm livre
  depois das folgas.
- Pente de pull-ups colado no CI (passo < 1 mm, sem vaga para via por pad) fica em F.Cu como leque curto; só a
  alimentação do pente desce para o polígono por uma via na ponta.
- **Todo pad de GND precisa da sua via** (o polígono de F.Cu não chega entre trilhas finas). Pad cercado → desviar
  ~0,5 mm a trilha vizinha para abrir a vaga (18/10, D411 do AIN); nunca via dentro do pad SMD.
- Fechou o bloco: `pcb_refill_zones` → `pcb_save` → DRC (0 violação nova, nenhuma rede pior) → `cantos.py --area`
  (0) → `render_semgnd.py` da área → mandar a imagem e relatar.

## Fase 5 — Ligações entre blocos, bornes e distribuição
1. Sinais entre blocos: rotas curtas, sem passar por dentro de outro bloco; respeitar zonas (analógico × ruidoso).
2. Bornes: contatos AC largos em F+B (5 A → ≥ 2,8 mm externa), dentro do keepout, com as folgas AC; sinais de campo
   pela cadeia de proteção.
3. **Alimentação na In2 como trilha larga** (ex. VIN_5G_RAW 1 mm); **polígono só quando a rede ramifica muito**
   ("só faz polígono quando tiver muita ramificação"). Vias de potência 0,8/0,4, várias em paralelo (≤ 1 A por via).
4. Header entre placas: conferir pino a pino com a outra placa.
5. Ao fim: 0 ligações faltando na placa.

## Regras de traçado
**Saída do pad** (20/10, Ecosnap: "essas trilhas saindo do lado do pad não me agrada, eu gostaria que tudo saísse do
meio do pad"): toda trilha começa/termina no **centro do pad** e sai pelo eixo dele; a curva vem depois de sair do
pad. Nunca encostar a trilha na lateral nem na ponta do pad (oblongo de borne, 0402, SOT, TSSOP). Trilha que corre
fora do eixo do pad entra com **desvio de 45° + 45°** (reta → diagonal até o eixo → reta até o centro, com ≥ 0,5 mm
reto antes do pad), não com canto em L. Conferir: `centro_pad.py` (0 pontas).
- **Tolerância 0,1 mm** (decisão minha, 20/10): abaixo disso o desalinhamento é invisível e corrigir obriga um "dente"
  de < 0,15 mm ou mover peça (o move do MCP apaga o 3D). Acima de 0,1 mm, centro sempre.
- Trilha que chega ao centro por um toco **dentro do próprio pad** já está certa.
- **Pad de potência/térmico** com os dois lados ≥ 1,5 mm (indutor, pad exposto, aba de MOSFET, suporte de bateria):
  a trilha entra pela borda mais próxima — ir ao meio do cobre não muda nada.
- **Desvio em S** (curvas opostas) pode ter diagonal ≥ 0,1 mm; os ≥ 0,5 mm entre curvas valem para curvas no mesmo
  sentido (90° disfarçado). `cantos.py` já segue isso.
- Pino de passo fino (0,5 mm, pad 0,3): a trilha de alimentação larga entra com o **último trecho em 0,2 mm** até o
  centro, senão a ponta encosta no pino vizinho (U501, Ecosnap).
- Barramento ligando pinos vizinhos do mesmo sinal (ex. COM_D de opto quádruplo): linha paralela fora da fileira e
  cada pino sobe reto do centro até ela; nada de ponte de canto a canto entre pads.
Correção em placa já roteada: `centro_pad_plano.py` (só lê o salvo; checa isolamento, ângulos e curvas; gera lote por
folha) → `teste_copia.py` de cada lote **e do conjunto** → MCP. O que ele não resolve se desenha à mão por padrão de
canal (Q80x, pente de pull-ups, opto) com `teste_copia` antes. Nunca apagar trilha sem repor.

**Ângulos**: só 0/45/90; **nenhum canto de 90°** e nenhum "90° disfarçado" (duas curvas de 45° coladas) — entre duas
curvas, ≥ 0,5 mm reto. Curva dentro do pad não conta.

**Stackup 4 camadas**: F sinal · In1 GND contínuo · In2 alimentação em trilhas largas (polígono só com muita
ramificação) + GND no resto · B sinal. GND nas 4 camadas. Não cruzar sinal sobre divisão de plano; via de GND a
≤ 5 mm de cada via de sinal que troca de camada.

**Largura** (IPC-2152, 1 oz, ΔT 10 °C, externa): 0,5 A 0,12 · 1 A 0,3 · 2 A 0,8 · 3 A 1,4 · 4 A 2,0 · 5 A 2,8 mm;
interna ≈ 2,6× e JLC 4L interna é 0,5 oz. Via 0,3/0,6 ≤ 1 A. JLC: sinal 0,2/0,2, alimentação ≥ 0,4, cobre↔borda
≥ 0,5 (regra do projeto). ESP32: alimentação ≥ 25 mil.

**Pares**: USB 90 Ω ≈ 0,21/0,13 · Ethernet 100 Ω ≈ 0,17/0,15 (JLC04161H-7628), sem via, sem stub, curtos.

**Folga por tensão** (fontes em `kicad-ia-tools/pcb/REGRAS_ROTEAMENTO.md`): IPC-2221C (230 Vac = 325 Vpk: externa c/
máscara 1,6 mm); IEC 60664-1: contato↔contato de relé ≥ 1,5 mm no ar / 2,5 mm superfície; rede ↔ SELV reforçada
≥ 6 mm em todas as camadas; rasgo só conta com ≥ 1 mm de largura. Isolação funcional de RS485 isolado: 4 mm (decisão
dele, Ecosnap). **Jumper/0 Ω entre redes AC** (ex. seletor de snubber NA/NF): footprint com pads ≥ 1,5 mm de folga
(1206 ou maior) — 0402 deixa 0,44 mm e trava o roteamento.
