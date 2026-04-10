# {{PROJECT_NAME}} — Technical Design v0.1

## 1. Database Schema

<!-- Tabelas, colunas, tipos, relacionamentos, índices -->

### `users`

| Column | Type | Constraints |
|---|---|---|
| id | uuid | PK |
| email | varchar(255) | UNIQUE NOT NULL |
| password_hash | varchar(255) | NOT NULL |
| role | varchar(32) | NOT NULL DEFAULT 'user' |
| created_at | timestamptz | NOT NULL DEFAULT now() |
| updated_at | timestamptz | NOT NULL DEFAULT now() |
| deleted_at | timestamptz | NULL |

Indexes: `email` (unique), `deleted_at`

## 2. Module Breakdown

<!-- Quais módulos existem e o que cada um possui -->

### `auth`
- Endpoints: login, refresh, logout, me
- Responsabilidades: autenticação, emissão de JWT, validação de tokens
- Depende de: `users`

### `<outro_modulo>`
- Endpoints:
- Responsabilidades:
- Depende de:

## 3. Integration Points

<!-- APIs externas, scrapers, third-party -->

- **<Serviço 1>**: propósito, endpoint, auth method
- **<Serviço 2>**: propósito, endpoint, auth method

## 4. Background Jobs

<!-- O que roda em background / scheduled e por quê -->

| Job | Schedule | Propósito |
|---|---|---|
| | | |

## 5. Auth & Permissions Matrix

| Role | Pode ler | Pode criar | Pode editar | Pode deletar |
|---|---|---|---|---|
| admin | tudo | tudo | tudo | tudo |
| user | próprios dados | próprios dados | próprios dados | nenhum |

## 6. Deployment Topology

<!-- Onde cada componente roda, como se conectam -->

```
[Browser]
    ↓ HTTPS
[nginx :80] (frontend estático)
    ↓
[FastAPI :{{BACKEND_PORT}}] (uvicorn + gunicorn)
    ↓
[PostgreSQL :5432] (nativo, não containerizado)
```

- **Ambiente dev**: processos diretos (uvicorn --reload + vite dev), DB em {{DB_HOST}}
- **Ambiente prod**: Docker Compose (backend + frontend), DB nativo no servidor

## 7. Migrations Strategy

- Alembic para todas as mudanças de schema
- Toda migration tem `upgrade()` e `downgrade()`
- Testes de integração rodam contra banco real com rollback transacional

## 8. Testing Strategy

- **Unit**: services isolados com repositórios mockados (< 5s total)
- **Integration**: repositórios contra PostgreSQL de teste
- **API**: full request/response via `httpx.AsyncClient`
- **Frontend**: Vitest + React Testing Library
- **Coverage target**: services 100%, repositories 90%, components 80%
