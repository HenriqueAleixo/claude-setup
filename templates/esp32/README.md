# {{PROJECT_NAME}}

{{PROJECT_DESCRIPTION}}

## Hardware

- **MCU**: {{ESP32_VARIANT}}
- **Protocolos**: {{PROTOCOLS}}
- **Periféricos**: {{PERIPHERALS}}

## Build

```bash
pio run                   # compilar
pio run --target upload   # gravar no dispositivo
pio device monitor        # ver serial
```

## Testes

```bash
pio test -e native        # testes unitários em host
pio test -e esp32         # testes on-target
```

## Estrutura

```
{{PROJECT_NAME}}/
├── include/
│   └── config.h          # defines, timeouts, stacks, pinos
├── src/
│   ├── tasks/            # 1 task por periférico/protocolo
│   ├── drivers/          # HAL se necessário
│   ├── app_logic.cpp     # lógica pura (testável em native)
│   └── main.cpp
├── test/
│   ├── stubs/            # retornos fixos
│   ├── fakes/            # implementações simplificadas
│   └── mocks/            # verificação de chamadas
├── data/                 # LittleFS
└── platformio.ini
```
