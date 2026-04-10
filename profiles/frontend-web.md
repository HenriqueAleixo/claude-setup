# CLAUDE SYSTEM RULES — Frontend Web (Professional Mode)

You are generating production-grade frontend web applications.

Platform:
- React 18+ with TypeScript (strict mode)
- Vite as build tool
- Tailwind CSS v4
- shadcn/ui as component library (in `src/components/ui/`)
- TanStack Query for server state management
- React Router 7 (or TanStack Router) for routing
- React Hook Form + Zod for forms and validation
- lucide-react for icons
- Vitest + React Testing Library for tests
- Framer Motion for animations (when truly needed)

---

# ARCHITECTURE (MANDATORY)

Strict layering inside `src/`:

```
src/
├── api/              HTTP clients (axios/fetch wrappers per domain)
├── components/
│   ├── ui/           shadcn/ui primitives (Button, Input, Card, Dialog, ...)
│   └── <feature>/    Feature-specific composite components
├── pages/            Route-level screens (one file per route)
├── hooks/            Custom reusable hooks
├── types/            TypeScript interfaces shared across layers
├── utils/            Pure helpers (cn, formatters, validators)
├── lib/              Third-party integrations (queryClient, axios instance)
├── assets/           Static images, icons, fonts
├── App.tsx
└── main.tsx
```

Rules:
- `api/` is the ONLY layer that calls `fetch`/`axios` — components never fetch directly.
- `api/` exposes typed functions returning Promises with TypeScript types from `types/`.
- `hooks/` wraps TanStack Query calls (`useQuery`/`useMutation`) that consume `api/`.
- `pages/` compose components, never contain business logic beyond layout and data wiring.
- `components/<feature>/` contains small single-purpose widgets.
- `components/ui/` contains ONLY shadcn primitives — do NOT modify their API, extend via composition.

---

# ABSOLUTE PROHIBITIONS

NEVER:
- Use `any` type — prefer `unknown` and narrow, or define proper types
- Use default exports (only named exports for components)
- Use inline styles (`style={{...}}`) when a Tailwind class exists
- Use CSS modules or styled-components (Tailwind only)
- Use `useEffect` to fetch data (use TanStack Query)
- Use `FutureBuilder`-equivalent patterns (raw Promise + useState) for server state
- Use `useState` for server state (use TanStack Query cache)
- Use index as `key` in dynamic lists (only acceptable for static, never-reordered lists)
- Drill props more than 2 levels (use composition, context, or TanStack Query cache)
- Put business logic in components (extract to hooks or pure functions in `utils/`)
- Use global mutable variables for state
- Create "god components" — build method / JSX root with more than 150 lines total
- Nest JSX more than 4 levels deep (extract sub-components)
- Create components without proper TypeScript props interface
- Use `!` non-null assertion without a documented justification
- Catch generic `Error` without specific handling or rethrowing
- Import from the same layer in a way that creates cycles
- Hardcode colors, spacing, durations — use Tailwind tokens and CSS variables
- Use `px` values in Tailwind — use the spacing scale (`p-4`, `gap-2`, etc.)
- Use `String` concatenation for URLs (use `URL` or `URLSearchParams`)
- Use `localStorage` for sensitive data (tokens → httpOnly cookie or in-memory)
- Ignore `BuildContext`-equivalent lifecycle: don't use stale closures in async effects
- Use sync imports for large libs in small features (code-split with `React.lazy`)
- Skip accessibility attributes on interactive elements
- Use `<div onClick>` when a `<button>` is the semantically correct element

If any rule is broken, warn explicitly.

---

# SEPARATION OF CONCERNS (CRITICAL)

## `api/` Layer (Data Access)

Must:
- Export typed functions (`getProducts(): Promise<Product[]>`)
- Handle URL building (prefer `URL` / `URLSearchParams`)
- Map raw responses to strongly-typed domain models (via `types/`)
- Propagate errors with meaningful messages — no silent catches

Must NOT:
- Know about React, hooks, or components
- Cache data (TanStack Query handles that)
- Transform data for presentation (that belongs to pages/components)

## `hooks/` Layer (State + Side Effects)

Must:
- Wrap TanStack Query calls in custom hooks (`useProducts()`, `useProductMutation()`)
- Provide a clean, consistent API (`{ data, isLoading, isError, refetch }`)
- Use `queryKey` arrays consistently (`['products', filters]`)

Must NOT:
- Import React components
- Contain JSX
- Access `document`, `window` without guards for SSR contexts

## `pages/` Layer (Routes)

Must contain only:
- Layout composition using components
- Data wiring via custom hooks
- Route params parsing via router
- State management (only loading/error branches rendering)

Must NOT:
- Contain business logic
- Call `fetch`/`axios` directly
- Define styled components inline (use `components/`)

## `components/` Layer (Presentation)

Must contain only:
- Pure presentational logic — render props into JSX
- Event handlers that call callbacks passed via props
- Local UI state (`useState` for toggles, focus, hover)
- Proper TypeScript props interface

Must NOT:
- Fetch data (parent passes it in)
- Know about routes or navigation (parent handles)
- Contain more than one responsibility

---

# STATE MANAGEMENT RULES

Strict hierarchy of state decisions:

| State type | Where it lives | Tool |
|---|---|---|
| Server state (API data) | TanStack Query cache | `useQuery` / `useMutation` |
| URL state (filters, pagination, active tab) | URL search params | `useSearchParams` |
| Global client state (theme, user, feature flags) | Context + custom hook | `createContext` + `useContext` |
| Local UI state (modal open, input value, hover) | Component state | `useState` |
| Derived state | Computed from props/state | Plain JS — never store duplicated state |

Rules:
- NEVER store server data in `useState` / Context — always TanStack Query
- NEVER store URL-derivable state in component state (e.g., "current tab" → URL param)
- Mutations always invalidate or update the relevant query cache on success
- Use `queryKey` factories in `src/lib/queryKeys.ts` to avoid string duplication

---

# STYLING RULES (Tailwind)

- Use Tailwind utility classes — zero inline styles, zero custom CSS files beyond `index.css`
- Use the `cn()` helper (`src/utils/cn.ts`) for conditional class merging
- Responsive design with Tailwind breakpoints (`sm:`, `md:`, `lg:`, `xl:`)
- Use CSS variables from `tailwind.config.js` / `index.css` for design tokens
- Consistent spacing scale — stick to `p-1/2/3/4/6/8/12/16`, never invent arbitrary values
- Use semantic color tokens (`bg-primary`, `text-muted-foreground`) over raw palette (`bg-blue-500`)
- Dark mode via `dark:` prefix — use `class` strategy (`darkMode: 'class'`)
- Never use `!important` — if you need to override, reorder classes or restructure
- Animations: prefer Tailwind transitions (`transition-colors duration-200`) — reach for Framer Motion only for complex orchestration

---

# ACCESSIBILITY (WCAG AA MANDATORY)

Every interactive element must:
- Be reachable via keyboard (Tab order correct, Enter/Space activate)
- Have visible focus indicator (`focus-visible:ring-2`)
- Have proper ARIA role when not using semantic HTML
- Have meaningful label (text content or `aria-label` for icon-only buttons)

Every image must have `alt` text (empty `alt=""` for purely decorative).

Form inputs must:
- Have `<label>` with `htmlFor` linked to input `id`
- Show validation errors next to the field via `aria-describedby`
- Announce submit errors via `aria-live="polite"` region

Color contrast: 4.5:1 minimum for text (Tailwind's default color scale with semantic tokens satisfies this if used correctly).

Heading hierarchy: exactly one `<h1>` per page, no skipping levels (`h1 → h2 → h3`).

Modals / Dialogs: trap focus, close on Escape, return focus to trigger on close (shadcn `Dialog` handles this).

---

# REQUIRED STATES (EVERY ASYNC OPERATION)

Every screen that fetches data MUST render all 4 states explicitly:

| State | When | How |
|---|---|---|
| **Loading** | Data fetching | `<Skeleton>` matching final layout — NOT a spinner for primary content |
| **Empty** | Query succeeded, no data | Icon/illustration + message + CTA ("Criar primeiro item") |
| **Error** | Query failed | Icon + friendly message + "Tentar novamente" button calling `refetch()` |
| **Success** | Data loaded | Real content |

Never render `null` or a blank screen while loading — always communicate state.

Prefer shadcn's `Skeleton` component for loading states.

---

# FORMS (React Hook Form + Zod)

- Define the schema with Zod in the same file as the form component
- Infer TypeScript types from the schema (`type FormValues = z.infer<typeof schema>`)
- Register fields via `register()` for simple inputs, `Controller` for custom components
- Show inline validation errors via `formState.errors`
- Disable submit button while `formState.isSubmitting`
- On success: reset form, show toast, invalidate relevant queries
- On error: show error message, keep values so user can retry

---

# TESTING (MANDATORY)

## Unit Tests (Vitest)

- Pure functions in `utils/` → 100% coverage
- Custom hooks → test with `renderHook` from `@testing-library/react`
- Mock TanStack Query via a test `QueryClient` wrapper

## Component Tests (React Testing Library)

- Test behavior, NOT implementation
- Query elements by accessible role (`getByRole('button', { name: /save/i })`)
- NEVER use `querySelector` or test IDs unless absolutely necessary
- Test user interactions with `userEvent` (not `fireEvent`)
- Mock API layer via MSW (Mock Service Worker) — NOT individual fetch mocks

## Page Tests

- Wrap with test providers (`QueryClientProvider`, `BrowserRouter`)
- Test that each of the 4 required states (Loading/Empty/Error/Success) renders correctly
- Test navigation triggers and form submissions end-to-end within the page

Rules:
- 1 scenario per test
- Descriptive names: `should show retry button when fetch fails`
- Every test must be independent
- Use MSW handlers in `src/test/mocks/` for consistent API mocking
- No `sleep` — use `waitFor` / `findBy` queries
- No test should depend on execution order

---

# FILE NAMING CONVENTIONS

- Components: `PascalCase.tsx` (`ProductCard.tsx`)
- Hooks: `camelCase.ts` starting with `use` (`useProducts.ts`)
- Utils: `camelCase.ts` (`formatCurrency.ts`)
- Types: `camelCase.ts` (`product.ts`, exports `interface Product`)
- API clients: `camelCase.ts` per domain (`products.ts` exports `getProducts`, `createProduct`)
- Pages: `PascalCasePage.tsx` (`ProductListPage.tsx`)
- Tests: co-located as `<name>.test.ts(x)` next to source file

One component per file. Props interface named `{ComponentName}Props`.

---

# PERFORMANCE RULES

- Large lists (>50 items) must use virtualization (`@tanstack/react-virtual`)
- Images must use `loading="lazy"` for below-the-fold content
- Heavy libs (charts, rich text editors) must be code-split with `React.lazy` + `Suspense`
- Debounce search/filter inputs (300ms typical) before triggering queries
- Memoize expensive computations with `useMemo` — but measure first, don't pre-optimize
- Memoize callbacks passed to memoized children with `useCallback`
- Use `React.memo` only when profiling shows actual re-render cost

---

# AUTHENTICATION & SECURITY

- Store access tokens in memory (never `localStorage`) OR in httpOnly cookie (preferred)
- Refresh tokens in httpOnly cookie, rotated on refresh endpoint
- API base URL via environment variable (`VITE_API_URL`)
- Never log sensitive data (tokens, passwords, personal info)
- CSRF protection via same-site cookies + origin validation
- XSS: React escapes by default, but NEVER use `dangerouslySetInnerHTML` with unsanitized input

---

# LOGGING

- Development: `console.log` / `console.error` allowed
- Production: ship errors to monitoring (Sentry or equivalent)
- Never log user inputs or API responses containing PII
- Feature flag logs by environment (`import.meta.env.MODE`)

---

# RELIABILITY

- Global error boundary in `App.tsx` catches unhandled render errors
- Network errors handled at query/mutation level with user-friendly messages
- Retry strategy: TanStack Query default (3 retries with backoff) for queries, no auto-retry for mutations
- Offline awareness: show banner when `navigator.onLine === false`
- Optimistic updates for frequent mutations (toggle favorite, mark read) with rollback on error
- Confirm destructive actions with shadcn `AlertDialog`
- Show toast notifications for async action results (`sonner` or `shadcn toast`)

---

# RESPONSE FORMAT

When generating frontend code:
1. Brief architecture explanation (max 10 lines)
2. Show IN THIS ORDER:
   a. Types file (if new entities involved)
   b. API client function (if new endpoint consumed)
   c. Custom hook (TanStack Query wrapper)
   d. Component / page implementation
   e. Test file for the component / hook
3. Always render all 4 required states for async data
4. No unused abstractions
5. No invented frameworks or wrappers
6. Keep code deterministic, testable, and accessible

---

# LANGUAGE

- Code: English
- Comments: Portuguese
- Communication: Brazilian Portuguese

If architecture violates these rules, consider the solution invalid.

---

# VALIDATION AFTER CODE CHANGES (MANDATORY)

After ANY code change, always:
1. Run `npm run lint` (eslint — zero warnings)
2. Run `npm run typecheck` (tsc --noEmit)
3. Run `npm run test` (vitest)
4. All three must pass before considering the change complete

Never leave a code change without all checks passing.
