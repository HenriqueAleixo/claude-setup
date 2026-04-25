# CLAUDE SYSTEM RULES — ThingsBoard Fork (Professional Mode)

You are working on a **fork pesado** (heavy fork) of ThingsBoard CE. This is NOT a greenfield project — you modify an existing 500k+ LOC codebase that we sync periodically with upstream.

Platform:
- ThingsBoard CE source (`thingsboard/thingsboard@release-3.9.x` upstream)
- Java 17 (LTS) + Spring Boot 3.x + Hibernate / JPA
- Angular 16 + TypeScript + RxJS + Angular Material
- Maven (multi-module project) for backend + npm for `ui-ngx/`
- PostgreSQL 15 (or Cassandra optional, not used in our setup)
- Docker (custom Dockerfile inheriting from official base)
- Goal: customize visual + functional aspects while remaining able to merge upstream releases

---

# ARCHITECTURE (READ-ONLY OVERVIEW)

ThingsBoard is a Maven multi-module project. Critical modules:

```
thingsboard/                            (root pom.xml — multi-module)
├── application/                        Spring Boot main app (entrypoint)
├── common/                             Shared utilities, types, security
├── dao/                                Data access layer (PostgreSQL/Cassandra)
├── rest-client/                        Java client for TB REST API
├── rule-engine/                        Rule chain processing (visual editor)
├── transport/                          MQTT, HTTP, CoAP transport layers
├── ui-ngx/                             Angular frontend (Angular 16)
│   ├── src/assets/                     Logos, favicons, themes (REBRAND HERE)
│   ├── src/app/shared/components/      Shared components (header, login, etc)
│   ├── src/app/modules/                Feature modules (dashboard, devices, etc)
│   ├── angular.json                    Build config (base-href config here)
│   └── package.json
├── docker/                             Official Dockerfiles
├── msa/                                Microservice architecture (we don't use)
└── pom.xml
```

We DO NOT touch what we don't need to change. Surgical modifications only.

---

# WORKING WITH A FORK (CRITICAL)

## Branch strategy

```
upstream/release-3.9.x         ← upstream stable, we sync from here monthly
  └── main (origin)            ← our integration branch
       └── release-3.9-curtolab (origin) ← our deployable branch
            └── feat/*, fix/*  ← feature branches
```

Setup:
```bash
git remote add upstream https://github.com/thingsboard/thingsboard.git
git fetch upstream
git checkout -b release-3.9-curtolab upstream/release-3.9.x
git push -u origin release-3.9-curtolab
```

## Monthly upstream sync

```bash
git fetch upstream
git checkout release-3.9-curtolab
git checkout -b chore/sync-upstream-$(date +%Y-%m)
git merge upstream/release-3.9.x
# resolve conflicts (most should be in files marked with // CURTOLAB:)
mvn test                                   # ensure backend still works
cd ui-ngx && npm test && npm run build     # ensure front still builds
git push origin chore/sync-upstream-...
# open PR -> review -> merge to release-3.9-curtolab
```

## MARKING CUSTOMIZATIONS (NON-NEGOTIABLE)

**Every line/block of code we modify or add MUST be marked.** This is the SINGLE most important rule for fork sustainability.

### Java
```java
// CURTOLAB: hide tenant admin menu when not sysadmin
if (!user.isSystemAdministrator()) {
    return filteredMenu;
}
// /CURTOLAB
```

### Angular TypeScript
```typescript
// CURTOLAB: redirect to onboarding instead of dashboard for new tenants
if (response.isFirstLogin) {
  this.router.navigate(['/onboarding']);
  return;
}
// /CURTOLAB
```

### Angular HTML templates
```html
<!-- CURTOLAB: replace ThingsBoard logo with CurtoLab logo -->
<img src="assets/logo-curtolab.svg" alt="CurtoLab" />
<!-- /CURTOLAB -->
```

### SCSS
```scss
/* CURTOLAB: override primary color to match CurtoLab orange */
$primary-color: #e37e20;
/* /CURTOLAB */
```

### Maven / Gradle / config files
```yaml
# CURTOLAB: reduce default DB connection pool size for low-tier tenants
hikari:
  maximum-pool-size: 10
# /CURTOLAB
```

Rationale:
- Makes upstream merge conflicts trivially identifiable
- Allows `grep -rn 'CURTOLAB:'` to list all our changes
- Audits become possible
- Future devs understand what's "ours" vs "theirs"

NEVER modify a line without the marker. NEVER use vague markers like `// modified` or `// custom`.

## Customization log

Maintain `README-curtolab.md` at the repo root with:
- List of files we modified (with brief reason)
- List of files/assets we added (logo.svg, theme overrides, etc)
- List of features we removed/hid (Tenants menu, Edge integration UI, etc)
- Current upstream version we're synced to (`v3.9.2` etc)

Update on EVERY PR that touches TB code.

---

# ABSOLUTE PROHIBITIONS

NEVER:
- Modify code without `// CURTOLAB:` marker (or the language equivalent)
- Modify upstream files without a clear reason documented in `README-curtolab.md`
- Touch files inside `transport/`, `rule-engine/`, `dao/` unless absolutely necessary (highest merge-conflict risk)
- Push directly to `release-3.9-curtolab` — always via PR
- Skip `mvn test` before committing Java changes
- Skip `npm test` and `npm run build` before committing Angular changes
- Commit `node_modules/`, `target/`, `dist/`, `.idea/` (verify `.gitignore` covers)
- Commit secrets — `application.yml` template only, real values via env vars
- Override Spring Boot security defaults without explicit security review
- Disable CSRF, CORS, or auth middleware
- Bypass TB's permission system (`@PreAuthorize`, etc) for "convenience"
- Add new Maven dependencies without checking license + security advisories
- Add new npm packages without `npm audit` clean
- Use `sysadmin` JWT in client-facing code paths
- Expose `sysadmin` credentials in any container's env
- Modify TB's `applicationContext.xml`, `pom.xml` versions, or `package.json` engines without testing locally
- Use `git rebase` on shared branches (`main`, `release-3.9-curtolab`) — only on personal feature branches
- Force-push to `main` or `release-3.9-curtolab`

If any rule is broken, warn explicitly and refuse to commit.

---

# CUSTOMIZATION PATTERNS

## Frontend (Angular) rebranding

Files to customize for visual rebrand:

| File | Change |
|---|---|
| `ui-ngx/src/assets/logo.svg` | CurtoLab logo (light theme) |
| `ui-ngx/src/assets/logo-white.svg` | CurtoLab logo (dark theme) |
| `ui-ngx/src/assets/favicon.ico` | CurtoLab favicon |
| `ui-ngx/src/assets/favicon-32x32.png` | + sizes |
| `ui-ngx/src/index.html` | `<title>`, meta description, theme-color |
| `ui-ngx/src/theme.scss` | Primary palette → CurtoLab orange/teal |
| `ui-ngx/src/app/shared/components/header.component.html` | Logo references, esconder menus |
| `ui-ngx/src/app/modules/login/pages/login/login.component.html` | Login page rebrand |
| `ui-ngx/src/app/shared/menu/menu.service.ts` | Filter out menus we don't expose (Tenants, Edge, etc) |

Pattern: when changing a template, copy to `*.curtolab.html` if substantial, then conditionally render. Or modify in place with markers if minor.

## Backend (Java) endpoint additions

Add new REST endpoints in a separate package: `org.curtolab.controller`. NEVER add files to `org.thingsboard.*` packages — keeps our code isolated.

```
application/src/main/java/
├── org/thingsboard/...                (upstream — don't touch unless markers)
└── org/curtolab/                      (our additions)
    ├── controller/                    Custom REST controllers
    ├── service/                       Custom services
    └── config/                        Spring config beans we add
```

Wire via `@Configuration` class scanned in main app (one marker in upstream's `Application.java` to add `@ComponentScan`).

## Hiding features (vs deleting)

Prefer **hiding** over **deleting** upstream features. Hide via:
- Backend: feature flag in `application.yml` defaulting `false`, controller checks flag
- Frontend: menu service filters out items based on user/tenant config

Delete only if hiding is impossible AND the feature creates merge conflicts repeatedly.

## Adding tables/columns to PostgreSQL

Use **Liquibase migrations** in our own changelog file:

```
dao/src/main/resources/sql/curtolab/
└── changelog-curtolab.xml             (referenced from upstream changelog-master.xml)
    ├── 001-add-billing-fields.xml
    └── 002-add-audit-log.xml
```

NEVER modify upstream's existing changelogs (would conflict with upstream history).

---

# BUILD PROCESS (custom)

## Angular with `--base-href /iot/`

`ui-ngx/angular.json`:
```json
"build:curtolab": {
  "builder": "@angular-devkit/build-angular:browser",
  "options": {
    "baseHref": "/iot/",
    "outputPath": "target/dist-curtolab",
    "index": "src/index.html",
    "main": "src/main.ts",
    ...
  }
}
```

Command: `npm run build:curtolab` (add npm script aliasing).

## Custom Dockerfile

`docker/tb-curtolab.Dockerfile` (in our repo):
```dockerfile
# Stage 1: build Angular front with custom base-href
FROM node:20-alpine AS ui-builder
WORKDIR /app
COPY ui-ngx/package*.json ./
RUN npm ci
COPY ui-ngx/ ./
RUN npm run build:curtolab

# Stage 2: build Java with Maven
FROM maven:3.9-eclipse-temurin-17 AS app-builder
WORKDIR /app
COPY pom.xml .
COPY application/pom.xml ./application/
# ... copy other module poms ...
RUN mvn dependency:go-offline -B
COPY . .
COPY --from=ui-builder /app/target/dist-curtolab ./ui-ngx/target/generated-resources/public
RUN mvn package -DskipTests -pl application -am

# Stage 3: runtime (inherit from official)
FROM thingsboard/tb-postgres:3.9.2 AS runtime
COPY --from=app-builder /app/application/target/thingsboard-*.jar /usr/share/thingsboard/bin/thingsboard.jar
USER thingsboard
EXPOSE 8080 1883 8883 5683
```

Tag: `curtolab/tb-iot:3.9.x-cl<n>` (semver of TB upstream + `cl<n>` for our iteration).

## Local dev

```bash
# Start postgres only
docker compose -f docker/dev-stack.yml up postgres

# Run TB locally with Maven (faster than full Docker rebuild)
mvn spring-boot:run -pl application -Dspring-boot.run.profiles=dev

# Run Angular dev server
cd ui-ngx && npm start                    # http://localhost:4200 with proxy to TB

# Or run Angular with custom base-href for /iot/ testing
cd ui-ngx && npm run build:curtolab && cd .. && mvn spring-boot:run ...
```

---

# TESTING

## Backend (Java)

```bash
mvn test                                  # all tests
mvn test -pl application                  # only application module
mvn test -Dtest=MyTest                    # single test
```

Rules:
- DON'T modify upstream tests — they validate upstream behavior
- DO add tests for our additions in `org/curtolab/...test packages
- All our tests in `src/test/java/org/curtolab/`
- Failing upstream test on a branch we're modifying → likely a sign we broke something via merge conflict — investigate before pushing

## Frontend (Angular)

```bash
cd ui-ngx
npm test                                  # Karma + Jasmine (existing setup)
npm run lint                              # tslint
npm run build:curtolab                    # ensure custom build still works
```

Rules:
- DON'T modify existing component tests; add new ones for new behavior
- Add tests in `*.spec.ts` co-located with source
- Test the `// CURTOLAB:` blocks we add

## Integration test before any push

ALWAYS run before push to `release-3.9-curtolab`:
```bash
mvn clean install -DskipTests=false      # full test suite, ~10min
cd ui-ngx && npm run build:curtolab      # custom front build
docker build -t curtolab/tb-iot:test -f docker/tb-curtolab.Dockerfile .
docker run --rm -p 8080:8080 curtolab/tb-iot:test
# manually verify http://localhost:8080/iot/ loads correctly
```

---

# REBRAND CHECKLIST

Track in `README-curtolab.md`. Initial pass:

- [ ] `ui-ngx/src/assets/logo.svg` (light)
- [ ] `ui-ngx/src/assets/logo-white.svg` (dark)
- [ ] `ui-ngx/src/assets/favicon.ico` + PNG sizes
- [ ] `ui-ngx/src/index.html` `<title>`, meta description, theme-color
- [ ] `ui-ngx/src/theme.scss` primary/accent colors
- [ ] `ui-ngx/src/app/shared/components/header.component.*` — esconder sysadmin menus, customizar
- [ ] `ui-ngx/src/app/modules/login/pages/login/login.component.*` — rebrand login
- [ ] `ui-ngx/src/app/shared/menu/menu.service.ts` — filter menu items
- [ ] `ui-ngx/src/app/locale/locale.constant-pt_BR.ts` — overrides PT (se quisermos custom)
- [ ] `application/src/main/resources/templates/*.email.html` — email templates
- [ ] `application/src/main/resources/application.yml` — branding fields (mail sender, etc)
- [ ] Grep + replace strings "ThingsBoard" → "CurtoLab" onde fizer sentido (NÃO em comentários técnicos do upstream)

---

# PRE-COMMIT HOOKS

`.pre-commit-config.yaml` (recommended):

```yaml
repos:
  - repo: https://github.com/zricethezav/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=1000']
```

Install: `pre-commit install`. Run: `pre-commit run --all-files` before push.

---

# PUSHING IMAGES

Registry: GitHub Container Registry (ghcr.io)

```bash
docker login ghcr.io -u henriquealeixo --password-stdin <<< "$GHCR_TOKEN"
docker tag curtolab/tb-iot:3.9.2-cl1 ghcr.io/henriquealeixo/curtolab-tb-iot:3.9.2-cl1
docker tag curtolab/tb-iot:3.9.2-cl1 ghcr.io/henriquealeixo/curtolab-tb-iot:latest
docker push ghcr.io/henriquealeixo/curtolab-tb-iot:3.9.2-cl1
docker push ghcr.io/henriquealeixo/curtolab-tb-iot:latest
```

Pull privado em produção via GHCR token configurado no Docker daemon da VPS.

---

# COMMIT CONVENTIONS

Branch: `feat/<short-name>`, `fix/<short-name>`, `chore/<short-name>`, `docs/<short-name>`

Commit format (Conventional Commits, in PT):
```
feat: adiciona menu customizado pra esconder Tenants
fix: corrige base-href em assets do Angular custom
chore: sync upstream v3.9.2
docs: atualiza README-curtolab com nova lista de assets
refactor: extrai endpoint billing pra org.curtolab.controller
```

PR description deve ter:
- Resumo do que mudou
- Por que (referência issue se houver)
- Como testar (passos manuais ou comando automatizado)
- Lista de arquivos com `// CURTOLAB:` adicionados/modificados
- Confirmação que `mvn test` e `npm run build:curtolab` passam

---

# LANGUAGE

- Code: English
- Comments (markers + docs custom): Portuguese
- Communication: Brazilian Portuguese
- README-curtolab.md: Portuguese
- Upstream files já em English — não traduzir

---

# VALIDATION AFTER CODE CHANGES (MANDATORY)

After ANY code change, always:

1. **Markers presentes**: `grep -rn 'CURTOLAB:' <files-changed>` → confirma TODA mudança tem marker
2. **Backend tests**: `mvn test -pl <module-changed>`
3. **Frontend build**: `cd ui-ngx && npm run build:curtolab` (não só `npm run build`)
4. **Docker build**: `docker build -f docker/tb-curtolab.Dockerfile .` (sanity check)
5. **README-curtolab.md atualizado** com novo arquivo modificado/feature
6. **Pre-commit hooks** passam: `pre-commit run --all-files`
7. **Manual smoke**: subir o container, abrir `/iot/`, validar visualmente que mudança apareceu sem quebrar nada

Nunca commitar sem todos esses passos. Reverter > comitar quebrado.

---

# WHEN IN DOUBT

- Não sabe se modificar é OK? → Adicione em `org.curtolab.*` (Java) ou novo arquivo (Angular) em vez de tocar upstream
- Conflito de merge upstream? → Investiga TODO marker `CURTOLAB:` na área de conflito; se ambíguo, peça review
- Feature do TB que queremos remover completamente? → Esconda primeiro (feature flag); só remova se for fonte recorrente de conflito
- Performance regrediu após nossa mudança? → `mvn -pl application test -Dtest=*Performance*` + profiling antes de aceitar
