# {{PROJECT_NAME}}

{{PROJECT_DESCRIPTION}}

## Stack

- **Backend**: FastAPI + SQLAlchemy 2.0 async + PostgreSQL
- **Frontend**: React + Vite + TypeScript + Tailwind + shadcn/ui + TanStack Query
- **Auth**: JWT (OAuth2 password flow)
- **Migrations**: Alembic
- **Testes**: pytest (backend) + Vitest (frontend)
- **Deploy**: Docker Compose

## Setup inicial

```bash
# 1. Copiar variáveis de ambiente
cp .env.example .env
# Editar .env com as suas credenciais

# 2. Backend
make dev              # instalar deps de dev
make migrate          # rodar migrations
make run              # subir backend em localhost:{{BACKEND_PORT}}

# 3. Frontend (em outro terminal)
cd frontend
npm install
npm run dev           # subir frontend em localhost:{{FRONTEND_PORT}}
```

## Comandos úteis

```bash
make help             # lista todos os targets
make check            # lint + typecheck + test (antes de commit)
make test             # rodar testes backend
make migrate-new msg="add users table"   # criar nova migration
```

## Estrutura

```
{{PROJECT_NAME}}/
├── backend/
│   ├── app/
│   │   ├── core/           # config, database, security, logging
│   │   ├── models/         # SQLAlchemy ORM
│   │   ├── schemas/        # Pydantic v2
│   │   ├── modules/        # domínios (router/service/repository)
│   │   └── main.py
│   ├── migrations/         # Alembic
│   └── tests/
├── frontend/
│   └── src/
│       ├── api/            # clientes HTTP
│       ├── components/     # componentes React
│       ├── pages/          # rotas
│       ├── hooks/          # TanStack Query wrappers
│       └── types/          # TypeScript
├── docs/
│   ├── PRD.md              # Product Requirements
│   └── TECHNICAL_DESIGN.md # Arquitetura
└── Makefile
```

## Documentação

- [docs/PRD.md](docs/PRD.md) — requisitos do produto
- [docs/TECHNICAL_DESIGN.md](docs/TECHNICAL_DESIGN.md) — desenho técnico
