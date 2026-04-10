---
name: docs-structure
description: Gera documentação da estrutura completa do código do projeto
---

Analise o código-fonte do projeto atual e gere/atualize a documentação da estrutura interna do projeto.

## O que documentar

Busque no código e documente TUDO que encontrar das categorias abaixo:

### 1. Árvore de Arquivos
- Gere um mapa visual estilo `tree` de diretórios e arquivos do projeto
- Descrição curta de cada arquivo/pasta
- Indique o papel de cada um: **task**, **driver**, **lógica pura**, **config**, **teste**, **dados**
- Ignore diretórios gerados (`.pio/`, `node_modules/`, etc.)

### 2. Tasks FreeRTOS
Para cada task encontrada no código (`xTaskCreate`, `xTaskCreatePinnedToCore`):
- **Nome** da task (parâmetro `pcName`)
- **Arquivo** onde está definida
- **Prioridade** (valor numérico + justificativa conforme tabela: Low 1-2, Medium 3, High 4-5)
- **Stack size** (macro de `config.h` usada)
- **Queues/EventGroups** que usa (envio e recebimento)
- **Mutexes** que adquire
- **Responsabilidade** resumida (1 linha)

### 3. Fluxo de Dados
Gere um diagrama em **Mermaid** (`graph LR` ou `graph TD`) mostrando:
- Tasks como nós
- Queues como setas com label (nome da queue e tipo de dado)
- EventGroups como conexões tracejadas com bits documentados
- Mutexes como anotações nos recursos compartilhados
- Direção do fluxo de dados
- ISRs como nós com formato especial, se existirem

### 4. Módulos e Funções Públicas
Para cada arquivo `app_*.cpp` / `app_*.h` e headers em `include/`:
- **Arquivo**
- **Responsabilidade** do módulo (1 linha)
- Lista de **funções públicas**:
  - Assinatura (nome, parâmetros, retorno)
  - Descrição curta
- **Dependências** (o que cada módulo importa/usa)

## Formato de Saída

Gerar o arquivo `DOCS_STRUCTURE.md` na **raiz do projeto** com o seguinte formato:

```markdown
# Estrutura do Projeto — [Nome do Projeto]

> Gerado automaticamente. Última atualização: [data]

## Árvore de Arquivos

\`\`\`
project/
├── include/
│   └── config.h          — Constantes, macros de stack/timeout/buffer
├── src/
│   ├── tasks/
│   │   └── task_mqtt.cpp  — Task de comunicação MQTT
│   ├── app_logic.cpp      — Lógica pura (state machine, validação)
│   └── main.cpp           — Inicialização e criação de tasks
├── test/
│   └── ...
└── platformio.ini
\`\`\`

---

## Tasks FreeRTOS

| Task | Arquivo | Prioridade | Stack | Responsabilidade |
|------|---------|------------|-------|------------------|
| mqtt_task | src/tasks/task_mqtt.cpp | 3 (Medium — protocolo) | MQTT_TASK_STACK | Publicação e assinatura MQTT |

### mqtt_task
- **Prioridade:** 3 (Medium — protocolo de comunicação)
- **Stack:** `MQTT_TASK_STACK` (4096 bytes)
- **Queues:** Recebe de `g_sensor_queue`, envia para `g_status_queue`
- **EventGroups:** Aguarda `WIFI_CONNECTED_BIT`
- **Mutexes:** `g_spi_mutex` (acesso ao barramento SPI)

---

## Fluxo de Dados

\`\`\`mermaid
graph LR
    ISR_SENSOR["ISR Sensor"] -->|g_sensor_queue| TASK_SENSOR["sensor_task"]
    TASK_SENSOR -->|g_data_queue| TASK_MQTT["mqtt_task"]
    TASK_MQTT -->|g_status_queue| TASK_DISPLAY["display_task"]
\`\`\`

---

## Módulos e Funções Públicas

### app_logic.h
**Responsabilidade:** Lógica pura de processamento de dados

| Função | Retorno | Descrição |
|--------|---------|-----------|
| `logic_validate_reading(float value, float min, float max)` | `bool` | Valida se leitura está dentro da faixa |

**Dependências:** nenhuma (módulo puro)
```

## Regras

- Só documentar o que **realmente existe no código** — não inventar
- Extrair prioridades, stacks, queues e mutexes **do código real**
- Se uma seção não tem conteúdo (ex: projeto sem Modbus task), **omitir a seção**
- Manter o arquivo `DOCS_STRUCTURE.md` — não sobrescrever outros arquivos
- Escrever em **português**
- O diagrama Mermaid deve refletir **apenas** conexões encontradas no código
- Incluir timestamp de geração no cabeçalho
