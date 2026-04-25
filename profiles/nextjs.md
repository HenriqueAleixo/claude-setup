# CLAUDE SYSTEM RULES — Next.js (App Router) (Professional Mode)

You are generating production-grade Next.js applications.

Platform:
- Next.js 14+ (App Router only — no `pages/`)
- TypeScript (strict mode)
- Tailwind CSS v3+ (or v4 if available)
- shadcn/ui as component library (in `src/components/ui/`)
- next-intl for i18n (server + client)
- React Hook Form + Zod for client forms; Zod for Server Action validation
- lucide-react for icons
- Playwright for E2E tests; Vitest for utility/Server Action helpers
- next/font (Google fonts via swap)
- @tanstack/react-query (only on client when needed for live data) — Server Components fetch directly

---

# ARCHITECTURE (MANDATORY)

App Router with route groups for layouts:

```
src/
├── app/
│   ├── [locale]/                  Locale-prefixed routes (next-intl)
│   │   ├── (marketing)/           Public routes (landing, /about, /pricing)
│   │   │   ├── layout.tsx         Marketing layout (no auth)
│   │   │   └── page.tsx
│   │   ├── (auth)/                Auth routes (signup, login, reset)
│   │   │   ├── layout.tsx         Auth layout (centered, no nav)
│   │   │   ├── signup/page.tsx
│   │   │   ├── login/page.tsx
│   │   │   └── actions.ts         Server Actions for auth
│   │   ├── (app)/                 Authenticated routes (dashboard, settings)
│   │   │   ├── layout.tsx         App layout (with auth check + nav)
│   │   │   ├── dashboard/page.tsx
│   │   │   └── billing/page.tsx
│   │   └── layout.tsx             Root locale layout (i18n provider, fonts, html lang)
│   ├── api/                       Route Handlers (only when frontend needs server endpoints; AVOID — prefer external API)
│   └── globals.css                Tailwind base + design tokens
├── components/
│   ├── ui/                        shadcn primitives (Button, Input, Card, Dialog, ...)
│   └── <feature>/                 Feature components
├── lib/
│   ├── api.ts                     Typed client for external API (FastAPI/etc)
│   ├── auth.ts                    Server-only auth helpers (getCurrentUser, requireAuth)
│   ├── cookies.ts                 Server-side cookie helpers (typed)
│   └── utils.ts                   Pure helpers (cn, formatters)
├── hooks/                         Custom hooks (only for Client Components)
├── types/                         Shared TS types
├── i18n/
│   ├── config.ts                  locales, defaultLocale
│   ├── request.ts                 getRequestConfig (server)
│   └── navigation.ts              createNavigation (Link, useRouter, usePathname)
├── middleware.ts                  next-intl middleware + auth gates
└── messages/                      pt.json, en.json (i18n strings)
```

Rules:
- **Server Components are the default.** Add `"use client"` ONLY when you need: hooks (`useState`, `useEffect`, `useReducer`), browser APIs (`window`, `document`, `localStorage`), or event handlers (`onClick`, `onChange`).
- **Forms use Server Actions** (`"use server"`) — not client-side fetch. Validate input with Zod inside the action.
- **Auth = httpOnly cookie** set via Server Action / Route Handler; read via `cookies()` from `next/headers` in Server Components or middleware.
- **Fetch in Server Components**: use native `fetch()` (cached automatically) or call your typed `lib/api.ts` client.
- **Fetch in Client Components**: use `useSWR` or `@tanstack/react-query` — never raw `useEffect` + `fetch`.
- **Mutations**: Server Action triggers fetch; on success, call `revalidatePath()` or `revalidateTag()` to refresh cache.
- **i18n**: every text comes from `useTranslations()` (client) or `getTranslations()` (server). No hardcoded strings in JSX.

---

# ABSOLUTE PROHIBITIONS

NEVER:
- Use `pages/` directory (App Router only)
- Add `"use client"` to a layout or page that doesn't actually need client-side interactivity
- Use `useState` / `useEffect` for server data — use Server Components or TanStack Query/SWR
- Fetch data inside Client Components without TanStack Query / SWR
- Use `Math.random()`, `new Date()`, `crypto.randomUUID()`, or `Date.now()` directly in Server Components — they cause **hydration mismatch**. Use `dynamic({ ssr: false })`, or initialize state empty and populate inside `useEffect`.
- Store auth tokens in `localStorage` or non-`httpOnly` cookies (XSS vulnerable)
- Use `router.push` from `next/router` (deprecated in App Router) — use `useRouter` from `next/navigation` (Client) or `redirect()` from `next/navigation` (Server)
- Define API routes inside `app/api/` if there's a separate backend service — call the backend directly from Server Components
- Use default exports for components (named exports only) — exception: `page.tsx`, `layout.tsx`, `loading.tsx`, `error.tsx`, `not-found.tsx`, `route.ts` MUST be default export (Next.js convention)
- Use `any` type — prefer `unknown` and narrow, or define proper types
- Use inline styles when a Tailwind class exists
- Use CSS modules or styled-components (Tailwind only)
- Use `next/image` `src` from a remote without configuring `images.remotePatterns` in `next.config.mjs`
- Mutate cookies inside Server Components (only allowed in Server Actions and Route Handlers — Server Components are read-only)
- Use `"use server"` and `"use client"` directives in the same file
- Skip `revalidatePath` / `revalidateTag` after a mutation that affects fetched data (UI shows stale data)
- Hardcode locales — read from `useLocale()` or route params
- Use `dangerouslySetInnerHTML` with unsanitized input
- Catch generic `Error` without specific handling or rethrowing
- Drill props more than 2 levels (use composition, server fetch, or context)
- Hardcode colors, spacing, durations — use Tailwind tokens and CSS variables
- Use `px` arbitrary values in Tailwind — stick to spacing scale (`p-4`, `gap-2`)
- Skip accessibility attributes on interactive elements
- Use `<div onClick>` when a `<button>` is the semantically correct element

If any rule is broken, warn explicitly.

---

# SERVER vs CLIENT (CRITICAL)

## Server Components (default)

Use for:
- Pages that render data from API/DB (Server Components fetch directly)
- Layouts that compose other components without browser interaction
- Anything that benefits from RSC streaming and zero client JS

Capabilities:
- `await fetch(...)` directly (auto-cached unless opted out)
- Read cookies via `cookies()` from `next/headers`
- Read headers via `headers()` from `next/headers`
- Use `redirect()` and `notFound()` from `next/navigation`
- Use `getTranslations()` from `next-intl/server`

Limitations:
- NO hooks (`useState`, `useEffect`, `useReducer`, `useContext`, etc.)
- NO browser APIs
- NO event handlers
- CANNOT mutate cookies (only Server Actions / Route Handlers can)

## Client Components (`"use client"` directive)

Use for:
- Interactive forms (with Server Actions still preferred for submission)
- Anything that needs `useState`, `useEffect`, or React Context
- Components using browser APIs (`window`, `document`, `localStorage`, `IntersectionObserver`)
- Components with event handlers (`onClick`, `onChange`, etc.)

Capabilities:
- All React hooks
- Browser APIs (with SSR guards: `if (typeof window !== 'undefined')`)
- Event handlers
- Interactive state

Limitations:
- Cannot use `cookies()`, `headers()`, `redirect()` from `next/headers` and `next/navigation` server APIs
- All client code ships to the browser — keep small

## Server Actions (`"use server"` directive)

Use for:
- Form submissions (signup, login, create/update entities)
- Mutations that need to set cookies or call external APIs server-side
- Actions that should `revalidatePath` / `revalidateTag` after success

Pattern:
```typescript
// app/[locale]/(auth)/actions.ts
"use server";

import { z } from "zod";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

const signupSchema = z.object({
  email: z.string().email(),
  password: z.string().min(12),
  name: z.string().min(2).max(100),
});

export async function signupAction(formData: FormData) {
  const parsed = signupSchema.safeParse({
    email: formData.get("email"),
    password: formData.get("password"),
    name: formData.get("name"),
  });

  if (!parsed.success) {
    return { error: parsed.error.flatten() };
  }

  const res = await fetch(`${process.env.API_URL}/auth/signup`, {
    method: "POST",
    body: JSON.stringify(parsed.data),
    headers: { "content-type": "application/json" },
  });

  if (!res.ok) return { error: { message: "Signup failed" } };

  const { token } = await res.json();
  (await cookies()).set("session", token, {
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    maxAge: 60 * 60 * 24 * 30, // 30d
  });

  redirect("/onboarding");
}
```

---

# DATA FETCHING

## Server Components: native `fetch`

```typescript
// Server Component
async function DashboardPage() {
  const data = await fetch(`${process.env.API_URL}/dashboard/stats`, {
    headers: { authorization: `Bearer ${(await cookies()).get("session")?.value}` },
    next: { tags: ["dashboard-stats"], revalidate: 30 },
  });
  const stats = await data.json();
  return <Dashboard stats={stats} />;
}
```

Cache control:
- `cache: "no-store"` for always-fresh data (never cached)
- `next: { revalidate: 60 }` for time-based revalidation (60s)
- `next: { tags: ["x"] }` for tag-based revalidation (call `revalidateTag("x")` from a Server Action)

## Client Components: SWR or TanStack Query

```typescript
"use client";
import useSWR from "swr";

export function LiveDevices() {
  const { data, error, isLoading } = useSWR("/api/devices/live", fetcher, {
    refreshInterval: 5000,
  });
  // ...
}
```

NEVER use raw `useEffect + fetch` — handles loading/error/cache poorly, prone to race conditions.

## Mutations

Server Action → external API → `revalidatePath` or `revalidateTag` → optionally `redirect`.

```typescript
"use server";
export async function createDevice(formData: FormData) {
  const res = await fetch(...);
  if (!res.ok) return { error: "..." };
  revalidateTag("devices");
  return { success: true };
}
```

---

# AUTHENTICATION (httpOnly cookies)

Pattern:
1. **Login/Signup** (Server Action) → call backend API → receive JWT → set as httpOnly cookie
2. **Middleware** (`src/middleware.ts`) → check cookie on protected routes → redirect `/login` if missing
3. **Server Components** → read cookie via `cookies()` → pass token in fetch `Authorization` header
4. **Client Components** → never see token; use SWR/TanStack Query against backend that reads cookie

Cookie config (always):
```typescript
{
  httpOnly: true,
  secure: true,            // HTTPS only
  sameSite: "lax",         // CSRF protection
  maxAge: <seconds>,
  path: "/",
}
```

Middleware example:
```typescript
// src/middleware.ts
import { NextResponse } from "next/server";
import createIntlMiddleware from "next-intl/middleware";
import { routing } from "@/i18n/navigation";

const intlMiddleware = createIntlMiddleware(routing);

export default function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const session = request.cookies.get("session")?.value;

  // Protect (app)/* routes
  const isAppRoute = /^\/(pt|en)\/(app|dashboard|billing|onboarding)/.test(pathname);
  if (isAppRoute && !session) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return intlMiddleware(request);
}

export const config = {
  matcher: ["/((?!api|_next|_vercel|.*\\..*).*)"],
};
```

---

# i18n (next-intl)

Setup:
- `messages/pt.json` and `messages/en.json` with flat key namespace
- `src/i18n/config.ts` exports `locales` and `defaultLocale`
- `src/i18n/request.ts` exports `getRequestConfig` for server
- `src/i18n/navigation.ts` exports `Link`, `useRouter`, `usePathname` (locale-aware)
- `src/middleware.ts` uses `createMiddleware(routing)`

Usage:
- **Server Components**: `import { getTranslations } from "next-intl/server"; const t = await getTranslations();`
- **Client Components**: `import { useTranslations } from "next-intl"; const t = useTranslations();`

Rule: **NO hardcoded strings in JSX.** Every label, button text, error message comes from messages.

---

# HYDRATION (CRITICAL — common source of bugs)

Hydration mismatch happens when SSR HTML doesn't match the first client render. Causes:

1. **Random values in SSR**: `Math.random()`, `crypto.randomUUID()` → different on server vs client
2. **Time-dependent values**: `new Date()`, `Date.now()` → server time ≠ client time
3. **Browser-only state**: `window.innerWidth`, `localStorage.getItem()` → `undefined` on server
4. **Locale-dependent formatting**: `Number.toLocaleString()` without explicit locale → server/client locale mismatch

Solutions (in order of preference):

1. **Move to client-only via `dynamic({ ssr: false })`**:
   ```typescript
   import dynamic from "next/dynamic";
   const ParticleField = dynamic(() => import("./ParticleField"), { ssr: false });
   ```

2. **Initialize state empty, populate in `useEffect`**:
   ```typescript
   const [data, setData] = useState<number[]>([]);
   useEffect(() => {
     setData(generateInitialData()); // uses Math.random
   }, []);
   ```

3. **Use `mounted` flag pattern**:
   ```typescript
   const [mounted, setMounted] = useState(false);
   useEffect(() => setMounted(true), []);
   if (!mounted) return null;
   ```

4. **Pass values from server explicitly** when possible (best for stable values).

NEVER use `suppressHydrationWarning` to hide bugs — only for cases where mismatch is expected and harmless (e.g., timestamp displayed inside `<time>`).

---

# STYLING (Tailwind + shadcn/ui)

- Use Tailwind utility classes — zero inline styles, zero custom CSS files beyond `globals.css`
- Use the `cn()` helper (`src/lib/utils.ts`) for conditional class merging
- Responsive design with Tailwind breakpoints (`sm:`, `md:`, `lg:`, `xl:`)
- CSS variables in `globals.css` for design tokens (colors, spacing); never duplicate raw values
- Use semantic color tokens (`bg-primary`, `text-muted-foreground`) over palette (`bg-blue-500`)
- Dark mode via `dark:` prefix — `class` strategy if used (in `tailwind.config.ts`)
- Animations: prefer Tailwind transitions (`transition-colors duration-200`)
- shadcn/ui components live in `src/components/ui/` — extend via composition, never modify primitive APIs

---

# SEO + METADATA

Every page that's user-facing must export `metadata`:

```typescript
import type { Metadata } from "next";
export const metadata: Metadata = {
  title: "Title — Brand",
  description: "...",
  openGraph: { title: "...", description: "...", images: ["/og.png"] },
};
```

For dynamic routes, use `generateMetadata`:

```typescript
export async function generateMetadata({ params }): Promise<Metadata> {
  const { id } = await params;
  const item = await fetchItem(id);
  return { title: item.name };
}
```

Root layout sets `<html lang>` from locale (next-intl).

---

# ACCESSIBILITY (WCAG AA MANDATORY)

Every interactive element must:
- Be reachable via keyboard (Tab order correct, Enter/Space activate)
- Have visible focus indicator (`focus-visible:ring-2`)
- Have proper ARIA role when not using semantic HTML
- Have meaningful label (text content or `aria-label` for icon-only buttons)

Every image must have `alt` text (empty `alt=""` for decorative).

Form inputs must:
- Have `<label>` with `htmlFor` linked to input `id`
- Show validation errors via `aria-describedby`
- Announce submit errors via `aria-live="polite"` region

Color contrast: 4.5:1 minimum for text.

Heading hierarchy: exactly one `<h1>` per page, no skipping levels.

Modals/Dialogs: trap focus, close on Escape, return focus to trigger (shadcn `Dialog` handles this).

---

# REQUIRED STATES (every async data render)

Server Components with async fetch must handle:
- **Success**: render content
- **Error**: throw → `error.tsx` boundary catches and shows friendly message + retry
- **Loading** (during streaming): use `loading.tsx` in same folder for Suspense fallback
- **Empty**: render empty state with icon + message + CTA when data array is empty

For Client Components fetching with SWR/TanStack Query: same 4 states explicitly.

Use shadcn's `Skeleton` component for loading states matching final layout — NOT spinners for primary content.

---

# FORMS

## Pattern: Server Action + Client form (with React Hook Form for UX)

```typescript
"use client";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { signupSchema, signupAction } from "./actions"; // schema can be shared

export function SignupForm() {
  const form = useForm({ resolver: zodResolver(signupSchema) });
  const [error, setError] = useState<string | null>(null);

  const onSubmit = form.handleSubmit(async (values) => {
    const formData = new FormData();
    Object.entries(values).forEach(([k, v]) => formData.append(k, v));
    const result = await signupAction(formData);
    if (result?.error) setError(result.error.message);
  });

  return <form onSubmit={onSubmit}>...</form>;
}
```

Rules:
- Schema shared between client (RHF) and server (validation in Server Action)
- Server Action validates AGAIN — client validation is UX, not security
- Disable submit button while submitting (`form.formState.isSubmitting`)
- Show inline validation errors via `formState.errors`
- On success: reset form + toast + revalidate cache (or `redirect()` from action)
- On error: show error message, keep values

---

# TESTING

## E2E Tests (Playwright) — primary

For pages, navigation, auth flows, payment flows.

- Tests in `tests/e2e/` at repo root
- Test `npm run dev` server (or production build)
- Use `page.getByRole`, `page.getByLabel` (accessible queries)
- Mock external APIs at network level when needed (`page.route`)
- Run in CI on push to main

## Unit Tests (Vitest) — secondary

Only for:
- Pure helpers in `lib/` and `lib/utils.ts`
- Server Action logic that can be extracted into pure functions
- Zod schemas (parse + validate)

Don't use Vitest to test Server Components or Client Components — too brittle. Use Playwright instead.

## Rules
- 1 scenario per test
- Descriptive names
- Independent tests
- No `sleep` — Playwright waits with `await expect(...).toBeVisible()`

---

# FILE NAMING

- Components: `PascalCase.tsx` (`SignupForm.tsx`)
- Hooks: `camelCase.ts` starting with `use` (`useDevices.ts`)
- Utils/lib: `camelCase.ts` (`formatCurrency.ts`)
- Types: `camelCase.ts` (`device.ts`, exports `interface Device`)
- API client: `camelCase.ts` per domain (`devices.ts`)
- Pages: ALWAYS named `page.tsx` (Next.js convention)
- Layouts: ALWAYS named `layout.tsx`
- Server Actions: `actions.ts` (one per route group typically)
- Tests E2E: `tests/e2e/<feature>.spec.ts`
- Tests unit: co-located `<name>.test.ts`

One component per file. Props interface named `{ComponentName}Props`.

---

# PERFORMANCE

- Heavy client libs (charts, rich text editors) → `dynamic({ ssr: false, loading: ... })`
- Images → `next/image` always (lazy by default, optimized)
- `next/font` for fonts (auto self-hosted, zero CLS)
- Server Components by default = less client JS
- Streaming with Suspense for slow data (wrap slow fetches in `<Suspense>`)
- Avoid client-side data fetching when Server Component fetch + revalidate suffices
- Profile build with `npm run build` and check bundle sizes

---

# AUTHENTICATION & SECURITY

- httpOnly cookies for session (set via Server Action, NEVER `localStorage`)
- `secure: true`, `sameSite: "lax"` (CSRF protection)
- Backend API key via env (`API_KEY`) — never expose to client
- `NEXT_PUBLIC_*` env vars are client-visible — only put non-sensitive there
- Sanitize any user input rendered with `dangerouslySetInnerHTML` (avoid entirely if possible)
- CSP header set in `next.config.mjs` headers or middleware
- Validate all Server Action inputs with Zod (don't trust client)

---

# LOGGING

- Server Components / Server Actions: `console.error` for errors → captured by Sentry
- Client: errors caught in error boundaries → `Sentry.captureException`
- NEVER log user inputs containing PII or tokens
- Production: `@sentry/nextjs` integrated in `instrumentation.ts`

---

# ERROR HANDLING

- `error.tsx` per route group catches uncaught errors during render → friendly UI + reset button
- `not-found.tsx` per route catches 404s
- `global-error.tsx` at root catches errors in root layout
- Server Actions return `{ error: ... }` for expected errors, `throw` for unexpected (caught by error boundary)
- Client Components: error boundaries from `react-error-boundary` or shadcn pattern

---

# DEPLOYMENT

- Build with `npm run build` — uses `output: "standalone"` in `next.config.mjs` for Docker
- Multi-stage Dockerfile: `node:20-alpine` base, `USER node` non-root, copy `.next/standalone` + `public` + `static`
- Env vars passed via Docker compose or platform (Vercel/Railway/etc)
- Healthcheck endpoint: usually root `/` or dedicated `/api/health` route handler
- Static assets cached aggressively (`Cache-Control: public, max-age=31536000, immutable`)

---

# RESPONSE FORMAT

When generating Next.js code:
1. Brief explanation (max 8 lines): what's Server vs Client, why
2. Show in this order:
   a. Types/Zod schemas (if new entities)
   b. Server Action (if mutation involved)
   c. Server Component / Page implementation
   d. Client Components (if needed)
   e. Test (Playwright spec or Vitest)
3. Always render all 4 required states for async data
4. Mark every Client Component clearly with `"use client"` at top
5. Mark every Server Action with `"use server"` at top
6. No invented frameworks; use what's in the platform list above

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
2. Run `npm run typecheck` (or `tsc --noEmit`)
3. Run `npm run build` (Next.js build catches more than typecheck — RSC violations, etc.)
4. Run E2E tests if affected: `npm run test:e2e`
5. All four must pass before considering the change complete

Never leave a code change without all checks passing.
