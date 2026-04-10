# {{PROJECT_NAME}} — Product Requirements Document (PRD) v0.1

## 1. Problem Statement

<!-- Qual problema este sistema resolve? Para quem? Por que agora? -->

## 2. Objectives

<!-- Metas mensuráveis. Exemplo: "reduzir tempo de consulta manual de 2h/dia para 0" -->

1.
2.
3.

## 3. User Stories

<!-- Formato: "Como [papel], eu quero [ação] para que [benefício]" -->

- **US-01** —
- **US-02** —
- **US-03** —

## 4. Scope (MVP)

### Dentro do escopo

-
-
-

### Fora do escopo (V2+)

-
-
-

## 5. Domain Model

<!-- Entidades principais e relacionamentos. Pode ser texto ou diagrama. -->

```
Entity1 ──has many──> Entity2
         ↓
         belongs to
         ↓
       Entity3
```

## 6. API Surface

<!-- Endpoints principais agrupados por módulo -->

### `/api/v1/auth`
- `POST /login`
- `POST /refresh`
- `POST /logout`

### `/api/v1/<domain>`
- `GET /` — listar
- `POST /` — criar
- `GET /:id` — detalhe
- `PATCH /:id` — atualizar
- `DELETE /:id` — remover

## 7. Non-functional Requirements

- **Performance**:
- **Security**:
- **Availability**:
- **Scalability**:
- **Auditability**:

## 8. Risks and Open Questions

- **Risco 1**:
- **Pergunta em aberto 1**:
- **Dependência externa 1**:
