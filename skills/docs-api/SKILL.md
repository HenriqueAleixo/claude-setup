---
name: docs-api
description: Gera documentação de APIs, MQTT, Modbus e Webhooks do projeto
---

Analise o código-fonte do projeto atual e gere/atualize a documentação técnica de comunicação.

## O que documentar

Busque no código e documente TUDO que encontrar das categorias abaixo:

### 1. Endpoints HTTP/REST
Para cada endpoint encontrado, documentar:
- **Rota** (ex: `GET /api/status`)
- **Método** (GET, POST, PUT, DELETE)
- **Autenticação** (se houver)
- **Payload de Request** (JSON com exemplo)
- **Payload de Response** (JSON com exemplo)
- **Códigos de retorno** (200, 400, 404, 500, etc.)

### 2. Tópicos MQTT
Para cada tópico encontrado, documentar:
- **Tópico** (ex: `device/sensor/temperature`)
- **Direção** (Publish / Subscribe)
- **QoS** (0, 1 ou 2)
- **Payload** (JSON com exemplo)
- **Frequência** (a cada Xs, por evento, etc.)
- **Retain** (sim/não)

### 3. Registradores Modbus
Para cada registrador encontrado, documentar:
- **Endereço** (ex: 0x0001)
- **Tipo** (Holding Register, Input Register, Coil, Discrete Input)
- **Leitura/Escrita** (R, W, R/W)
- **Tipo de dado** (uint16, int32, float, etc.)
- **Unidade** (°C, %, bar, etc.)
- **Descrição**

### 4. Webhooks
Para cada webhook encontrado, documentar:
- **URL** de destino
- **Método** (POST/PUT)
- **Payload** (JSON com exemplo)
- **Headers** (Content-Type, Auth, etc.)
- **Códigos de resposta esperados**

## Formato de Saída

Gerar o arquivo `DOCS_API.md` na **raiz do projeto** com o seguinte formato:

```markdown
# Documentação de Comunicação — [Nome do Projeto]

> Gerado automaticamente. Última atualização: [data]

## Endpoints HTTP

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | /api/status | Retorna status do dispositivo |

### GET /api/status
**Autenticação:** Basic Auth
**Response:**
\`\`\`json
{ "exemplo": "aqui" }
\`\`\`

---

## Tópicos MQTT
(se encontrado)

## Registradores Modbus
(se encontrado)

## Webhooks
(se encontrado)
```

## Regras

- Só documentar o que **realmente existe no código** — não inventar
- Extrair exemplos de payload **do código real** (ArduinoJson, strings, etc.)
- Se uma categoria não existir no projeto, omitir a seção
- Manter o arquivo `DOCS_API.md` — não sobrescrever outros arquivos
- Escrever em **português**
