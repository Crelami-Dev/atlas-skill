# Bug Hunting Checklist

Use this checklist to systematically examine every layer of the project during discovery.

## 1. Functional Logic and Edge Cases

- Boundary inputs: `0`, negative numbers, `NaN`, `Infinity`, empty strings `""`, whitespace-only strings, single-element arrays, and oversized payloads.
- Null/None/Undefined dereferencing: optional chaining gaps, missing dictionary keys, uninitialized component state, or empty query results (`first()` returning `None`).
- Off-by-one errors in pagination (`limit`/`offset`, page 0 vs page 1), loop bounds, and date/time ranges.
- Floating-point precision bugs in financial calculations, discounts, taxes, or totals.
- Timezone mismatches: mixing naive and timezone-aware timestamps, local browser dates vs UTC backend dates.

## 2. State Management and Concurrency

- Double-submission bugs: clicking submit buttons twice rapidly without disabling state or idempotency guards.
- Async race conditions: out-of-order network responses overwriting newer UI state, stale closures in hooks/callbacks, missing `await` on async calls.
- Shared mutable state across requests, workers, or default function arguments (e.g., mutable default `def fn(items=[])` in Python).
- Memory and resource leaks: unclosed file descriptors, database connections, WebSocket listeners, `setInterval` timers, or event subscriptions.

## 3. API Contracts and Data Layer

- Frontend-backend payload drift: mismatched field names (`camelCase` vs `snake_case`), wrong HTTP methods/status codes, or missing required fields.
- Missing database transactions: partial writes leaving orphaned or inconsistent records when step 2 of a multi-step operation fails.
- N+1 query bottlenecks or unbounded queries missing pagination that hang on realistic dataset sizes.
- Migration/schema mismatches between ORM models and SQL migrations.

## 4. Error Handling and Resilience

- Swallowed exceptions (`catch {}` or `except: pass`) that silently report success when an operation failed.
- Unhandled promise rejections or uncaught exceptions that crash the entire server process.
- External API call failures without timeouts, retry limits, or graceful fallback states in the UI.
- Broken loading, empty, or error UI states leaving users stuck on infinite spinners.

## 5. Build, Environment, and Cross-Platform Compatibility

- Hardcoded local paths (`/Users/...`, `C:\...`), hardcoded ports, or missing environment variable defaults/validation at startup.
- Case-sensitive file import mismatches (`./Header` vs `./header.tsx`) that pass on macOS/Windows but fail on Linux production servers.
- Missing or mismatched peer dependencies and build script errors.
