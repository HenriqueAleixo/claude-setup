---
name: gen-readme
description: Gera README.md completo para projetos de firmware ESP32
---

Analise o código-fonte do projeto atual e gere/atualize o `README.md` na raiz do projeto.

## O que incluir

Extraia do código real e monte as seções abaixo:

### 1. Cabeçalho
- **Nome do projeto** (extrair do `platformio.ini` ou nome da pasta)
- **Descrição curta** (1-2 linhas, baseada no que o firmware faz)
- **Badges** (se aplicável): plataforma, framework, versão do PlatformIO

### 2. Visão Geral
- O que o projeto faz (3-5 linhas)
- Plataforma/board alvo (extrair de `platformio.ini` → `board`)
- Framework (Arduino/ESP-IDF)
- Protocolos de comunicação usados (WiFi, MQTT, HTTP, Modbus, BLE — extrair do código)

### 3. Hardware
- **Board** (extrair de `platformio.ini`)
- **Periféricos** usados (extrair dos includes e inicializações: SPI, I2C, UART, GPIO, ADC, etc.)
- **Pinagem** (extrair defines/constantes de pinos do `config.h` ou código)
- Tabela de conexões se houver pinos documentados

### 4. Arquitetura
- Diagrama Mermaid resumido mostrando as tasks e fluxo principal de dados
- Lista de tasks com responsabilidade (1 linha cada)
- Separação lógica pura vs. tasks (mencionar brevemente)

### 5. Dependências
- Listar **todas as bibliotecas** de `platformio.ini` → `lib_deps`
- Para cada uma: nome e propósito no projeto
- Versão se especificada

### 6. Configuração
- Parâmetros configuráveis via NVS/Preferences (SSID, IP, tokens — extrair do código)
- Parâmetros de `config.h` que o usuário pode querer ajustar
- Variáveis de ambiente se houver

### 7. Build e Flash
```
# Compilar
pio run

# Flash
pio run --target upload

# Monitor serial
pio device monitor

# Testes unitários
pio test -e native
```

### 8. Estrutura de Diretórios
- Árvore resumida (estilo `tree`) com descrição curta de cada pasta/arquivo principal
- Não detalhar cada arquivo — só a visão geral

### 9. Endpoints / Comunicação (resumo)
- Se houver API HTTP: listar rotas principais (sem detalhe — referenciar `DOCS_API.md`)
- Se houver MQTT: listar tópicos principais (sem detalhe — referenciar `DOCS_API.md`)
- Se houver Modbus: mencionar e referenciar `DOCS_API.md`

### 10. Testes
- Como rodar os testes (`pio test -e native`)
- Breve descrição do que é testado
- Referenciar pasta `test/`

## Formato de Saída

Gerar o arquivo `README.md` na **raiz do projeto**:

```markdown
# Nome do Projeto

Descrição curta do que o firmware faz.

## Visão Geral

Firmware para ESP32-S3 que [faz X, Y e Z]. Comunica via [MQTT/HTTP/Modbus] com [sistema externo].

- **Board:** ESP32-S3 DevKitC
- **Framework:** Arduino (PlatformIO)
- **Protocolos:** WiFi, MQTT, HTTP

## Hardware

| Periférico | Pino | Descrição |
|------------|------|-----------|
| LED Status | GPIO2 | Indicação de estado |
| Sensor SPI | GPIO5 (CS) | Leitura de dados |

## Arquitetura

\`\`\`mermaid
graph LR
    SENSOR["sensor_task"] -->|g_data_queue| MQTT["mqtt_task"]
    MQTT -->|g_status_queue| DISPLAY["display_task"]
\`\`\`

| Task | Prioridade | Responsabilidade |
|------|------------|------------------|
| sensor_task | 4 (High) | Aquisição de dados |
| mqtt_task | 3 (Medium) | Publicação MQTT |

## Dependências

| Biblioteca | Versão | Uso |
|------------|--------|-----|
| PubSubClient | ^2.8 | Cliente MQTT |
| ArduinoJson | ^7.0 | Serialização JSON |

## Configuração

Parâmetros ajustáveis via portal web / NVS:
- `WIFI_SSID` — Rede WiFi
- `MQTT_BROKER` — IP do broker MQTT

Constantes em `include/config.h`:
- `SENSOR_READ_INTERVAL_MS` — Intervalo de leitura (padrão: 1000)

## Build e Flash

\`\`\`bash
# Compilar
pio run

# Flash
pio run --target upload

# Monitor serial
pio device monitor

# Testes
pio test -e native
\`\`\`

## Estrutura do Projeto

\`\`\`
├── include/config.h       — Constantes e macros
├── src/
│   ├── tasks/             — Tasks FreeRTOS
│   ├── app_logic.cpp      — Lógica pura
│   └── main.cpp           — Inicialização
├── test/                  — Testes unitários
├── data/                  — Arquivos LittleFS
└── platformio.ini
\`\`\`

## Comunicação

Documentação detalhada de APIs em [`DOCS_API.md`](DOCS_API.md).
Documentação da estrutura em [`DOCS_STRUCTURE.md`](DOCS_STRUCTURE.md).

## Testes

\`\`\`bash
pio test -e native
\`\`\`

Testes unitários em `test/` usando Unity framework. Testam lógica pura sem dependência de hardware.
```

## Regras

- Só documentar o que **realmente existe no código** — não inventar
- Extrair board, libs, pinos e protocolos **do código real** (`platformio.ini`, `config.h`, `src/`)
- Se uma seção não tem conteúdo, **omitir** (ex: se não tem Modbus, não mencionar)
- Se `DOCS_API.md` ou `DOCS_STRUCTURE.md` existirem, **referenciar** — não duplicar conteúdo
- Manter conciso — README é visão geral, não documentação exaustiva
- Escrever em **português**
- Incluir comandos de build/flash/teste sempre
- Não incluir informações sensíveis (senhas, tokens, IPs reais)
