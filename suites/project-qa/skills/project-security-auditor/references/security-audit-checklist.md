# Security Vulnerability Audit Checklist

Verify every applicable category below by tracing untrusted inputs, privilege checks, and configurations in the codebase.

## 1. Broken Access Control (OWASP A01)

- Object-level authorization (IDOR / BOLA): confirm every endpoint reading, editing, or deleting a resource by ID verifies resource ownership against the authenticated user session/token, never trusting `user_id` from request body/query.
- Function-level authorization: confirm admin, internal, or management routes enforce role middleware on the server side (not just hidden buttons in the frontend).
- Mass assignment / over-posting: confirm ORM `create`/`update` calls explicitly whitelist allowed fields so users cannot inject `role: "admin"`, `is_verified: true`, or `balance`.
- Path traversal: confirm file read/download/delete operations canonicalize paths (`realpath` / `resolve`) and enforce containment inside an allowed base directory.

## 2. Cryptographic Failures & Secrets Exposure (OWASP A02)

- Hardcoded API keys, database URLs, JWT signing secrets, SMTP credentials, or cloud keys in source files, frontend bundles (`NEXT_PUBLIC_*`, `VITE_*`), or committed `.env` files.
- Password storage: confirm `Argon2id`, `bcrypt`, or `scrypt` is used with proper work factors (never plaintext, MD5, SHA1, or unsalted SHA256).
- Sensitive data exposure in API responses (returning password hashes, tokens, or PII of other users in serializer objects) or verbose stack traces leaked to production clients.

## 3. Injection & Unsafe Execution (OWASP A03)

- SQL / NoSQL Injection: confirm parameterized queries or safe ORM bindings everywhere, including dynamic `ORDER BY`, `WHERE IN`, raw SQL blocks, and MongoDB `$where` / operator injection (`{"$ne": null}` in JSON inputs).
- Cross-Site Scripting (XSS): confirm stored and reflected user content is escaped, avoid raw `innerHTML` / `dangerouslySetInnerHTML` without strict HTML sanitization (e.g., DOMPurify), and validate `javascript:` URLs in user-supplied `href`/`src` links.
- Command & Template Injection: confirm user input never reaches shell commands (`shell=True`, `exec`), `eval`, or server-side template strings.

## 4. Authentication, Session & Rate Limiting (OWASP A07)

- JWT flaws: accepting `alg: none`, weak/default signing secrets, missing `exp`/`aud`/`iss` validation, or storing high-privilege tokens in XSS-accessible `localStorage` without mitigation.
- Session cookies: check `HttpOnly`, `Secure`, and `SameSite` attributes plus session regeneration on login/logout.
- Missing rate limiting or account lockout on login, OTP verification, password reset, and expensive public endpoints.
- Insecure password-reset or magic-link tokens (predictable `Math.random()`/`random.randint` instead of CSPRNG, missing expiration, or single-use invalidation).

## 5. CSRF, CORS, SSRF, File Uploads & Config (OWASP A05 / A08 / A10)

- CORS misconfiguration: reflecting arbitrary `Origin` headers or wildcard `*` paired with credentials.
- CSRF exposure on cookie-authenticated state-changing endpoints without CSRF tokens or strict `SameSite` protections.
- Server-Side Request Forgery (SSRF): user-controlled URLs fetched by backend HTTP clients without scheme/host allowlists and private IP (`127.0.0.1`, `169.254.169.254`, RFC1918) blocking.
- Unrestricted file upload: trusting client `Content-Type` or extension without server-side allowlisting, randomizing stored filenames, and preventing execution in public static folders.
- Missing HTTP security headers (`Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `Strict-Transport-Security`, `Frame-Options`) or debug mode (`DEBUG=True`) enabled in production config.
