# Padrão de placa: buck

- Laço quente mínimo: Cin no VIN, diodo/chave no SW, GND dos dois no mesmo ponto.
- Indutor fora do laço; nada sensível sob o indutor nem sob o nó SW.
- FB longe do SW; divisor de FB a ≤ 2–3 mm do pino.
- Nós VIN/SW/GND/VOUT em polígono sólido na F.Cu, prioridade alta (Fase 3).
- Perto da entrada e de uma borda (Fase 2).
