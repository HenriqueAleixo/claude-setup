# Fechamento — Fase 6

1. `pcb_refill_zones`, DRC 0 erro (ruído aceito: lib_footprint_mismatch, silk, starved_thermal de borne TH —
   relatar o número).
2. `cantos.py` sem curva > 45° e sem segmento < 0,5 mm entre duas curvas.
3. `centro_pad.py`: 0 ponta de trilha fora do centro do pad.
4. Referências ocultas (0 visíveis); peças novas sem DNP indevido.
5. Modelos 3D: contar `(model ` no arquivo; se caiu, com o pcbnew fechado (combinado com ele): `add3d.py`.
6. Imagem final (malha oculta + 3D se ele pedir), `pcb_save`, commit do projeto com o que mudou.
