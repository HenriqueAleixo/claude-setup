# claude-setup

Configuração pessoal do [Claude Code](https://claude.com/claude-code) para desenvolvimento de firmware ESP32, apps Flutter e sistemas full-stack (FastAPI + React).

Este repo centraliza **perfis**, **skills**, **agents** e **templates** que ficam disponíveis globalmente em qualquer sessão do Claude Code.

---

## Conceitos

Três coisas diferentes vivem aqui. Saber a diferença evita confusão:

| Tipo | O que é | Quando carrega | Onde mora |
|---|---|---|---|
| **Profile** (CLAUDE.md) | Regras de arquitetura, proibições, convenções — sempre ativas | Toda mensagem da sessão | `profiles/*.md` |
| **Skill** | Fluxo/gerador invocado sob demanda; guia o Claude passo a passo numa tarefa interativa | Quando trigger bate ou você invoca | `skills/<nome>/SKILL.md` |
| **Agent** | Claude "filho" com contexto isolado; delega uma subtarefa pesada e retorna resumo | Quando o Claude principal decide delegar | `agents/<nome>.md` |

**Regra prática:**
- Regra que vale **sempre que você programa** → profile
- Tarefa que você quer **acompanhar passo a passo e aprovar** → skill
- Tarefa que você quer **delegar e receber pronta** → agent

---

## Perfis disponíveis

| Perfil | Stack | Uso |
|---|---|---|
| [`profiles/esp32.md`](profiles/esp32.md) | PlatformIO + Arduino/ESP-IDF + FreeRTOS + C++17 | Firmware ESP32 (S2/S3/C3) |
| [`profiles/flutter.md`](profiles/flutter.md) | Flutter 3.x + Clean Arch + Bloc + TDD | Apps mobile Android/iOS |
| [`profiles/systems.md`](profiles/systems.md) | FastAPI async + SQLAlchemy 2.0 + PostgreSQL + Alembic | Backend Python |
| [`profiles/frontend-web.md`](profiles/frontend-web.md) | React 18+ + TS + Vite + Tailwind + shadcn/ui + TanStack Query | Frontend web |

Projetos full-stack importam **systems.md + frontend-web.md** juntos.

---

## Skills disponíveis

| Skill | Função |
|---|---|
| `init-project` | Bootstrap de projeto novo — detecta tipo, aplica template, cria CLAUDE.md com `@imports` |
| `prd` | Gera Product Requirements Document completo |
| `flutter-ui` | Consultor de UI/UX Flutter (telas, componentes, design system, review) |
| `docs-api` | Documenta APIs REST/MQTT/Modbus/Webhooks |
| `docs-structure` | Documenta estrutura de código |
| `gen-readme` | Gera README.md para projetos ESP32 |
| `gen-tests` | Gera testes unitários ESP32 (Memfault best practices) |
| `fullbin` | Gera binário completo ESP32 (bootloader + partitions + app + LittleFS) |
| `release` | Gera OTA, commita, pusha e cria release no GitHub |
| `ralph` | Converte PRDs para formato Ralph (prd.json) |

---

## Agents disponíveis

| Agent | Função |
|---|---|
| `design-iterator` | Refina UI web iterativamente com passes de polish (Stripe/Linear/Vercel refs) |
| `react-ui-engineer` | Implementador React+TS+Tailwind+shadcn+TanStack Query |
| `ui-reviewer` | Revisor de código frontend (antipatterns React, WCAG AA, performance) |

---

## Templates

`templates/` contém os scaffolds usados pela skill `init-project`:

- **`templates/systems/`** — Full-stack FastAPI+React estilo cc-radar (backend/app/, frontend/src/, Makefile, Dockerfiles, docs/PRD.md, docs/TECHNICAL_DESIGN.md)
- **`templates/esp32/`** — PlatformIO com include/config.h, src/tasks/, test/{stubs,fakes,mocks}/, platformio.ini multi-env
- **`templates/flutter/`** — Clean Architecture folders (lib/core/, lib/features/, injection_container.dart) sobre `flutter create`

Todos os templates usam placeholders `{{PROJECT_NAME}}`, `{{DB_NAME}}`, `{{BACKEND_PORT}}`, etc. que são substituídos pela skill `init-project`.

---

## Instalação

```bash
cd ~/.claude
git clone https://github.com/HenriqueAleixo/claude-setup.git dev-profiles
cd dev-profiles
./install.sh
```

O `install.sh` cria symlinks em `~/.claude/`:

- `~/.claude/profiles` → `dev-profiles/profiles`
- `~/.claude/skills` → `dev-profiles/skills`
- `~/.claude/agents` → `dev-profiles/agents`
- `~/.claude/CLAUDE.md` → `dev-profiles/profiles/esp32.md` (default)

Se já houver conteúdo em `~/.claude/{profiles,skills,agents}`, é movido para `~/.claude/backups/pre-install-<timestamp>/` antes do symlink.

---

## Uso

### Trocar o perfil ativo

```bash
ln -sfn ~/.claude/dev-profiles/profiles/flutter.md ~/.claude/CLAUDE.md
ln -sfn ~/.claude/dev-profiles/profiles/systems.md ~/.claude/CLAUDE.md
```

### Criar um projeto novo

Numa sessão do Claude Code:

> vamos criar um projeto novo

A skill `init-project` ativa automaticamente, pergunta tipo (ESP32/Flutter/Systems/Backend/Frontend), coleta metadados, mostra proposta, e só executa após sua aprovação.

### Usar um perfil em um projeto existente

Crie um `CLAUDE.md` na raiz do projeto com `@import`:

```markdown
# Meu projeto

@~/.claude/profiles/flutter.md

## Regras específicas
- <o que for diferente do perfil base>
```

O Claude Code expande o `@import` automaticamente.

---

## Contribuindo (consigo mesmo)

Quando criar um perfil, skill ou agent novo:

1. **Sempre dentro de `dev-profiles/`** (nunca direto em `~/.claude/` — seria perdido)
2. Commit + push pro repo — o symlink garante que as mudanças aparecem sem reinstalar
3. Em outra máquina: `git pull` e pronto

Edições podem ser feitas tanto em `~/.claude/profiles/*.md` quanto em `~/.claude/dev-profiles/profiles/*.md` — é o mesmo arquivo via symlink.

---

## Estrutura do repo

```
claude-setup/
├── README.md              (este arquivo)
├── install.sh             (script idempotente de symlinks)
├── .gitignore
├── profiles/              (4 perfis — regras sempre ativas)
├── skills/                (10 skills — fluxos sob demanda)
├── agents/                (3 agents — delegação com contexto isolado)
└── templates/             (scaffolds usados pela init-project)
    ├── systems/
    ├── esp32/
    └── flutter/
```
