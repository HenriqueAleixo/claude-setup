# CLAUDE SYSTEM RULES — Web/SaaS Systems (Professional Mode)

You are generating production-grade web systems.

Platform:
- Python 3.12+
- FastAPI (async)
- React 18+ with Vite + TypeScript (SPA)
- PostgreSQL
- SQLAlchemy 2.0 (async) + Alembic
- Docker + Docker Compose

---

# ARCHITECTURE (MANDATORY)

Clean Architecture in 3 layers:

```
Router (API) → Service (Business Logic) → Repository (Data Access)
```

Rules:
- Routers only handle HTTP: parse request, call service, return response.
- Services contain ALL business logic. Must be pure — no DB imports, no HTTP objects.
- Repositories are the ONLY layer that touches the database.
- Dependencies flow inward: Router → Service → Repository. Never reverse.
- Dependency injection via FastAPI `Depends()`.
- Each domain module follows this structure (e.g., `products/router.py`, `products/service.py`, `products/repository.py`).
- Async everywhere: all I/O operations must be async.

Communication between services:
- Direct function calls for synchronous flows.
- Background tasks (FastAPI BackgroundTasks or Celery) for async jobs.
- Never call a repository from another domain — go through the service.

---

# ABSOLUTE PROHIBITIONS

NEVER:
- Put business logic in routers/endpoints
- Import SQLAlchemy models in routers
- Write raw SQL outside repository layer
- Use `*` imports
- Use mutable default arguments
- Return SQLAlchemy models directly from endpoints (use Pydantic schemas)
- Store secrets in code (use environment variables)
- Use `print()` for logging (use structlog)
- Catch bare `except:` or `except Exception:` without re-raising or logging
- Use synchronous I/O in async context (no `requests`, use `httpx`)
- Use `datetime.now()` (use `datetime.now(UTC)`)
- Use Doxygen-style comments (`/** */`, `@param`, `@return`, `@brief`, `@file`). Use plain comments only (`#` or `//`)
- Commit `.env` files or secrets to git

If any rule is broken, warn explicitly.

---

# SEPARATION OF CONCERNS (CRITICAL)

## Services (Pure Logic)

Must:
- Be framework-independent (no FastAPI, no SQLAlchemy imports)
- Receive data as Pydantic models or primitive types
- Return Pydantic models or primitive types
- Be fully testable without database or HTTP
- Contain: validations, calculations, state machines, business rules, transformations

Must NOT:
- Access database directly
- Import ORM models
- Handle HTTP requests/responses
- Manage transactions (repository responsibility)

## Routers (API Layer)

Must contain only:
- Request parsing and validation (automatic via Pydantic)
- Dependency injection
- Calling service methods
- Returning responses with correct status codes

Must NOT:
- Contain business logic
- Contain data access logic
- Transform data beyond what Pydantic does automatically

## Repositories (Data Layer)

Must contain only:
- Database queries (SQLAlchemy)
- Transaction management
- Data mapping (ORM model ↔ domain types)

Must NOT:
- Contain business rules
- Validate business logic
- Return ORM models to services (convert to Pydantic/dataclass)

---

# CODE STRUCTURE

```
project/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py          # Pydantic Settings
│   │   │   ├── database.py        # SQLAlchemy engine + session
│   │   │   ├── security.py        # JWT + OAuth2 utilities
│   │   │   └── logging.py         # structlog configuration
│   │   ├── models/                # SQLAlchemy ORM models
│   │   ├── schemas/               # Pydantic request/response schemas
│   │   ├── modules/
│   │   │   └── <domain>/
│   │   │       ├── router.py
│   │   │       ├── service.py
│   │   │       ├── repository.py
│   │   │       └── exceptions.py
│   │   ├── middleware/
│   │   └── main.py
│   ├── migrations/                # Alembic
│   │   ├── versions/
│   │   └── env.py
│   ├── tests/
│   │   ├── unit/
│   │   │   └── test_<module>_service.py
│   │   ├── integration/
│   │   │   └── test_<module>_repository.py
│   │   ├── api/
│   │   │   └── test_<module>_router.py
│   │   ├── factories/
│   │   │   └── <module>_factory.py
│   │   └── conftest.py
│   ├── alembic.ini
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/                   # API client (httpx/fetch wrappers)
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── types/
│   │   ├── utils/
│   │   └── App.tsx
│   ├── tests/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── Dockerfile
├── docker-compose.yml
├── docker-compose.prod.yml
├── Makefile
└── .env.example
```

Naming conventions:
- Python: snake_case for everything (files, functions, variables)
- TypeScript: camelCase for variables/functions, PascalCase for components/types
- Database tables: snake_case, plural (e.g., `products`, `price_entries`)
- API endpoints: kebab-case (e.g., `/api/v1/price-entries`)
- No magic numbers — all constants in `config.py` or `.env`

---

# DATABASE RULES

- Alembic for ALL schema changes — never modify the database manually
- Every migration must be reversible (implement `downgrade()`)
- Use UUID as primary key (not auto-increment integer)
- Every table must have `created_at` and `updated_at` timestamps
- Soft delete with `deleted_at` column when business requires audit trail
- Indexes on all foreign keys and frequently queried columns
- Connection pooling configured in `database.py` (pool_size, max_overflow)
- Use async sessions (`AsyncSession`) everywhere
- Connection string via environment variable

---

# TESTING (TDD — MANDATORY)

## Methodology: Red-Green-Refactor

1. **RED:** Write a failing test FIRST
2. **GREEN:** Write minimum code to make it pass
3. **REFACTOR:** Clean up while keeping tests green

This cycle is mandatory for all new features and bug fixes.

## Test Structure

### Unit Tests (services)
- Test services in isolation with mocked repositories
- No database, no HTTP, no I/O
- Fast: entire suite < 5 seconds
- Use `pytest` + `pytest-asyncio`
- One test file per service: `test_<module>_service.py`

### Integration Tests (repositories)
- Test repositories against real PostgreSQL (test database)
- Use transactions that rollback after each test
- Use `factory_boy` to create test data
- One test file per repository: `test_<module>_repository.py`

### API Tests (routers)
- Test full request/response cycle
- Use `httpx.AsyncClient` with `app` fixture
- Test status codes, response schemas, auth, error cases
- One test file per router: `test_<module>_router.py`

### Frontend Tests
- Components: Vitest + React Testing Library
- Test behavior, not implementation
- Test user interactions, not internal state

## Test Rules
- 1 scenario per test function
- Test name describes the scenario: `test_calculate_margin_returns_zero_when_cost_equals_price`
- Every test must be independent (no shared mutable state)
- Use fixtures (`conftest.py`) for shared setup
- Use `factory_boy` factories — never create test data manually inline
- Every factory must have a `build()` method (in-memory) and `create()` method (persisted)
- No `sleep()` in tests
- No test should depend on execution order

## Fixtures Pattern (conftest.py)
```python
# Async database session fixture with rollback
# Async httpx client fixture
# Auth token fixture for authenticated tests
```

## Running Tests
```bash
# Tudo
make test

# Só unit
make test-unit

# Só integration
make test-integration

# Com cobertura
make test-cov
```

---

# API RULES

- All endpoints under `/api/v1/`
- Pydantic v2 schemas for ALL request/response bodies
- Use `status_code` explicitly on every endpoint
- Pagination: offset/limit with default limit=50, max limit=100
- Error responses: consistent JSON format `{"detail": "message", "code": "ERROR_CODE"}`
- Use FastAPI exception handlers for global error handling
- Rate limiting on public endpoints
- CORS configured in `main.py`

Schema naming:
- `<Entity>Create` — for POST body
- `<Entity>Update` — for PUT/PATCH body
- `<Entity>Response` — for response
- `<Entity>ListResponse` — for paginated list response

---

# AUTHENTICATION

- OAuth2 with password flow (FastAPI native)
- JWT access token: short-lived (15 minutes)
- JWT refresh token: long-lived (7 days), stored in httpOnly cookie
- Password hashing: bcrypt via `passlib`
- Role-based access: user, admin (extensible)
- Protected routes via `Depends(get_current_user)`
- Refresh endpoint: `/api/v1/auth/refresh`

---

# LOGGING

- Use `structlog` for structured JSON logging
- Every request: correlation_id (UUID) for tracing
- Log format: `{"timestamp", "level", "message", "correlation_id", "module", ...}`
- Log levels:
  - DEBUG: detailed internal state (dev only)
  - INFO: key events (startup, request summary, job completion)
  - WARNING: recoverable issues
  - ERROR: failures that need attention
- Never log sensitive data (passwords, tokens, full credit card numbers)
- Every module logs on start: `logger.info("module_initialized", module="<module_name>")`

---

# ENVIRONMENTS

## Development (local, no containers)
- Backend: `uvicorn --reload` running directly on dev machine
- Frontend: `vite dev` running directly on dev machine
- PostgreSQL: external server (no container), accessed via network
- No Docker in development — run processes directly for speed and simplicity
- Use `.env` for local configuration (DATABASE_URL, etc.)

## Production (Docker on server)
- Docker Compose for all application services (backend + frontend)
- Multi-stage Dockerfile builds (builder + runtime)
- Backend: gunicorn + uvicorn workers
- Frontend: nginx serving built static files
- PostgreSQL: external (native on server, NOT in container)
- Health checks on all services
- Restart policies: `unless-stopped`
- Resource limits defined

## Rules
- No `latest` tag — always pin versions
- `.dockerignore` must exclude: `.git`, `node_modules`, `__pycache__`, `.env`
- Secrets via environment variables, never baked into images
- Makefile commands for common operations:
  ```makefile
  make up        # docker compose up -d
  make down      # docker compose down
  make build     # docker compose build
  make logs      # docker compose logs -f
  make shell     # docker compose exec backend bash
  make migrate   # alembic upgrade head
  make test      # pytest
  ```

---

# RELIABILITY

- Health check endpoint: `GET /api/v1/health`
- Graceful shutdown handling
- Database connection retry on startup
- Background tasks must handle failures (retry + dead letter)
- External API calls: always with timeout + retry (httpx with tenacity)
- No overengineering
- No speculative abstraction
- No unnecessary wrapper layers

---

# RESPONSE FORMAT

When generating system code:
1. Brief architecture explanation (max 10 lines)
2. Show:
   - Test file FIRST (TDD)
   - Service/logic file
   - Router/repository as needed
   - Schema if new models involved
3. No unused abstractions
4. No invented frameworks
5. Keep code deterministic and testable

---

# LANGUAGE

- Code: English
- Comments: Portuguese
- Communication: Brazilian Portuguese

If architecture violates these rules, consider the solution invalid.

---

# PROJECT PLANNING (MANDATORY)

Every new system project MUST begin with a structured planning phase before any code is written.

## Phase 1: PRD (Product Requirements Document)

Before coding, produce a PRD containing:
1. **Problem Statement** — What problem does this system solve? For whom?
2. **Objectives** — Measurable goals (e.g., "reduce manual price checks from 2h/day to 0")
3. **User Stories** — Who does what, and why. Format: "As a [role], I want [action] so that [benefit]"
4. **Scope (MVP)** — What is IN the first version and what is explicitly OUT
5. **Domain Model** — Core entities and their relationships (text or diagram)
6. **API Surface** — Main endpoints, grouped by domain module
7. **Non-functional Requirements** — Performance, security, availability expectations
8. **Risks and Open Questions** — Known unknowns, dependencies, blockers

## Phase 2: Technical Design

After PRD approval, produce:
1. **Database Schema** — Tables, columns, types, relationships, indexes
2. **Module Breakdown** — Which domain modules exist, what each one owns
3. **Integration Points** — External APIs, scrapers, third-party services
4. **Background Jobs** — What runs on schedule or in background, and why
5. **Auth & Permissions Matrix** — Who can do what
6. **Deployment Topology** — Where each component runs, how they connect

## Phase 3: Implementation Order

Define a strict build order following these principles:
1. **Database models + migrations first** — foundation for everything
2. **Core module (auth, config, health)** — system boots and authenticates
3. **Domain modules one at a time** — each module: schema → repository → service → router → tests
4. **Frontend after backend APIs are stable** — avoid rework
5. **Integration/E2E tests after individual modules work** — test the full chain last

Each module follows the TDD cycle:
```
Write test → Make it pass → Refactor → Next test
```

## Planning Rules
- Never start coding without an approved PRD
- Never build a module without knowing its test scenarios
- Never build frontend before the API it consumes exists and is tested
- Scope creep: if a feature wasn't in the PRD, it goes to the next version
- Every planning artifact lives in `docs/` at the project root

---

# VALIDATION AFTER CODE CHANGES (MANDATORY)

After ANY code change, always:
1. Run `make lint` (ruff check + ruff format --check)
2. Run `make typecheck` (mypy)
3. Run `make test` (pytest)
4. All three must pass before considering the change complete

For frontend changes:
1. Run `npm run lint` (eslint)
2. Run `npm run typecheck` (tsc --noEmit)
3. Run `npm run test` (vitest)

Never leave a code change without all checks passing.
