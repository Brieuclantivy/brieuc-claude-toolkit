# Vulnerability checklist

Use as a map, not a script. For each class: does it apply to this stack? If yes, where are the sinks? Tag findings with CWE and OWASP Top 10 (2021) category when you know them.

## Contents
1. Secrets and sensitive data
2. Authentication and sessions
3. Authorization
4. Injection
5. Web client-side
6. Server-side request and file handling
7. Deserialization and unsafe evaluation
8. Cryptography
9. Business logic and concurrency
10. Availability
11. APIs (REST, GraphQL, WebSocket, webhooks)
12. Dependencies and supply chain
13. Configuration, infrastructure, CI/CD
14. Logging, errors, privacy
15. Stack-specific pitfalls
16. LLM / AI features

## 1. Secrets and sensitive data
- API keys, tokens, passwords, private keys, connection strings in code, config, `.env*` committed, test fixtures, docs, Docker images/build args, CI files.
- Same in **git history** and other branches/tags (`git log --all -p -S'password'`, deleted files).
- `.env` tracked or missing from `.gitignore`; example files containing real values.
- Secrets shipped to the browser (frontend bundles, `NEXT_PUBLIC_*`/`VITE_*` misuse, source maps).
- Hard-coded default/admin credentials, backdoor accounts, debug endpoints.
- Sensitive data stored in plaintext (passwords not hashed, PII, tokens), in localStorage, in URLs, in logs.

## 2. Authentication and sessions
- Password storage: must be bcrypt/argon2/scrypt with cost; not MD5/SHA1/unsalted.
- Login: user enumeration (different messages/timing), no rate limit/lockout, credential stuffing exposure.
- Password reset / email verification / invitation: predictable or non-expiring tokens, token reuse, token in referrer/logs, host header poisoning of reset links.
- MFA bypass paths, "remember me" tokens, OAuth/OIDC (missing `state`/PKCE, open redirect_uri, unverified email claims, account linking takeover).
- Sessions: fixation, missing regeneration after login, cookie flags (`HttpOnly`, `Secure`, `SameSite`), no expiry/logout invalidation.
- JWT: `alg: none`/algorithm confusion, weak/hard-coded secret, no `exp`, no audience/issuer check, sensitive data in payload, no revocation.
- API keys: no rotation, no scope, sent in query strings.

## 3. Authorization
- **Every** endpoint/handler/GraphQL resolver/WebSocket message/background job: is there an authn check *and* an ownership/role check?
- IDOR/BOLA: object ids taken from the request without verifying the caller owns them (read, update, delete, download, export).
- Function-level: admin routes reachable by normal users; role checked only in the UI.
- Mass assignment / over-posting: request body bound straight to models (`role`, `isAdmin`, `tenantId`, `price`).
- Multi-tenancy: queries missing tenant filter; shared caches keyed without tenant.
- Privilege escalation via profile update, invitation, role-change endpoints.
- Default-allow middleware, routes registered outside the protected group, method confusion (GET protected, POST not), path normalization bypasses.

## 4. Injection
- SQL (string concatenation, raw queries, `ORDER BY`/column/table names from input, ORM raw fragments), NoSQL operators (`$ne`, `$where`), LDAP, XPath, GraphQL.
- OS command (`exec`, `system`, `shell=True`, backticks, argument injection like `--option` in user-controlled args).
- Template injection (SSTI: Jinja2, Twig, Smarty, Freemarker, ERB, JS template strings).
- XXE in XML parsers (external entities enabled), XML bombs.
- Header/CRLF injection, email header injection, log injection, CSV/formula injection in exports.
- Expression/eval languages (SpEL, OGNL, EL), regex built from input.

## 5. Web client-side
- XSS: reflected, stored, DOM (`innerHTML`, `dangerouslySetInnerHTML`, `v-html`, `document.write`, `eval`, `href="javascript:"`, unsanitised Markdown/rich text, SVG uploads).
- CSRF on state-changing requests (cookie auth without token/SameSite), CORS misconfig (`*` with credentials, reflected origin, `null`).
- Missing/weak security headers (CSP, HSTS, X-Content-Type-Options, frame-ancestors/X-Frame-Options, Referrer-Policy, Permissions-Policy). Clickjacking.
- Open redirects (`next=`, `returnUrl=`), `postMessage` without origin checks, `target="_blank"` without `noopener`.
- Tokens in localStorage, sensitive data cached, source maps in production, third-party scripts without SRI.
- Unsafe deep links / WebView settings in mobile or Electron (`nodeIntegration`, `contextIsolation` off).

## 6. Server-side request and file handling
- SSRF: any URL fetched server-side from user input (webhooks, image/PDF fetchers, import-by-URL, link previews). Cloud metadata (169.254.169.254), internal hosts, DNS rebinding, redirects, `file://`, `gopher://`.
- Path traversal / LFI / RFI: user input in file paths, `include`/`require`, `sendFile`, archive extraction (Zip Slip), symlinks.
- File upload: extension/MIME/magic-byte checks, executable content served from the web root, size limits, image-processing libraries, stored under predictable public paths, SVG/HTML served inline.
- Unauthenticated static exposure of backups, `.git`, `.env`, dumps, logs, admin panels, directory listing.

## 7. Deserialization and unsafe evaluation
- PHP `unserialize`, Python `pickle`/`yaml.load`/`marshal`, Java `ObjectInputStream`/XStream/Jackson polymorphic typing, .NET `BinaryFormatter`, Ruby `Marshal`/`YAML.load`, Node `node-serialize`/`vm`.
- `eval`, `Function()`, `exec`, dynamic `require`/`import` from input, `pickle` in caches/queues.
- Prototype pollution (`merge`, `extend`, `set` on user-controlled keys, `__proto__`, `constructor`).

## 8. Cryptography
- Weak hashes/ciphers (MD5, SHA1, DES, RC4, ECB), homemade crypto, static/hard-coded keys and IVs, reused nonces.
- Non-cryptographic RNG for tokens/ids/passwords (`Math.random`, `rand`, `random`), predictable tokens.
- TLS verification disabled (`verify=False`, `rejectUnauthorized: false`, `InsecureSkipVerify`), outdated protocols.
- Timing-unsafe comparison of secrets/signatures, missing signature verification on webhooks.

## 9. Business logic and concurrency
- Race conditions (double spend, coupon reuse, limit bypass, TOCTOU on balance/stock/one-time tokens).
- Price/quantity/discount taken from the client, negative or overflowing numbers, currency rounding.
- State-machine bypass (skipping payment/approval steps), replay of one-time actions, forgotten-password flows abused for account takeover.
- Trust in client-supplied flags, hidden fields, feature toggles.
- Resource abuse: unlimited free trials, referral loops, email/SMS sending endpoints usable as spam relay.

## 10. Availability
- ReDoS (nested quantifiers on user input), unbounded pagination/`limit`, huge uploads/bodies, zip/XML/JSON bombs, GraphQL depth/complexity/aliases/batching, N+1 endpoints that amplify.
- Missing timeouts on outbound calls, unbounded queues/caches/memory growth, expensive endpoints without rate limit.
- (Analyse in code only; do not flood a running instance.)

## 11. APIs
- Excessive data exposure (full DB objects in responses: password hashes, tokens, other users' PII), verbose error bodies.
- GraphQL: introspection in prod, field-level auth, batching for brute force, depth limits.
- WebSocket/SSE: auth on connect *and* per message, origin checks (CSWSH).
- Webhooks: signature verification, replay protection, idempotency.
- API versions: old versions/undocumented routes with weaker checks; debug/health/metrics/actuator/swagger endpoints exposed.
- HTTP method override, content-type confusion, parameter pollution.

## 12. Dependencies and supply chain
- Known vulnerabilities (audit tools above; also check EOL runtimes/frameworks/base images).
- Lockfile missing or ignored, version ranges `*`/`latest`, git/URL dependencies, dependency confusion (private names on public registries), typosquats.
- Install/postinstall scripts, curl-pipe-bash in Dockerfiles or scripts, unverified downloads.
- Vendored/copy-pasted libraries with old versions.

## 13. Configuration, infrastructure, CI/CD
- Debug mode on, stack traces to clients, default credentials, permissive CORS, admin interfaces exposed, unused ports/services.
- Docker: running as root, `latest` tags, secrets in ENV/build args/layers, `--privileged`, docker.sock mounts, wide port bindings (`0.0.0.0` for DB/Redis), missing healthcheck/resource limits.
- Kubernetes / Terraform / CloudFormation: public buckets, `*` IAM policies, open security groups, unencrypted storage, secrets in manifests.
- CI/CD (GitHub Actions, GitLab CI...): `pull_request_target` with checkout of PR code, script injection through `${{ github.event... }}`, unpinned third-party actions, over-broad `permissions`, secrets exposed to forks, self-hosted runners.
- Database/cache/queue: no auth, default ports exposed, over-privileged DB user (app connects as root/superuser).
- Reverse proxy/web server: directory listing, exposed dotfiles/backups, host header trust, missing size/time limits.

## 14. Logging, errors, privacy
- Passwords/tokens/PII/card numbers in logs, analytics, error trackers; missing audit logs for sensitive actions.
- Error messages leaking internals (SQL, paths, versions).
- PII handling: retention, deletion, export, consent, data sent to third parties (GDPR relevance if EU users).

## 15. Stack-specific pitfalls (check those matching the stack)
- **PHP / CakePHP / Laravel / Symfony**: `unserialize`, `include` with input, type juggling (`==` on hashes/tokens), `extract`, `$_REQUEST`, register-globals-style patterns, CSRF component disabled, Security component gaps, `debug` > 0, mass assignment via `$fillable`/`patchEntity` without `accessibleFields`, raw SQL in query builder, unrestricted `Configure` exposure, `phpinfo`.
- **Node / Express / Nest / Next**: prototype pollution, `child_process` with input, `helmet` missing, `express.static` over broad paths, `cors()` defaults, unvalidated `req.body`, `eval`/`vm`, SSRF in `fetch`, Next.js server actions / API routes without auth, middleware-only auth (bypassable), secrets in `NEXT_PUBLIC_`.
- **Python / Django / Flask / FastAPI**: `DEBUG=True`, `SECRET_KEY` committed, `mark_safe`, `|safe`, `pickle`, `yaml.load`, `subprocess(shell=True)`, `ALLOWED_HOSTS=*`, `csrf_exempt`, raw SQL/`extra()`, Jinja `render_template_string`, Flask `debug=True` (Werkzeug console RCE).
- **Java / Spring**: actuator endpoints exposed, SpEL injection, deserialization, XXE defaults, `permitAll` patterns, CSRF disabled globally, Log4Shell-era versions.
- **Go**: `InsecureSkipVerify`, `text/template` vs `html/template`, path joins with input, goroutine data races on shared auth state, `unsafe`.
- **Rust / C / C++**: `unsafe` blocks, buffer/integer overflows, format strings, use-after-free, unchecked `unwrap` on input as DoS.
- **Ruby / Rails**: mass assignment (strong params), `html_safe`/`raw`, `send`/`constantize` on input, `Marshal`, `find_by_sql`, `redirect_to params[...]`.
- **Mobile / Electron / desktop**: exported components, insecure storage, cert pinning absent, deep link hijack, `nodeIntegration`.
- **SQL / DB migrations**: over-broad grants, RLS disabled (Supabase/Postgres), triggers/functions with `SECURITY DEFINER`.
- **Firebase / Supabase / BaaS**: permissive rules (`allow read, write: if true`), service-role key in client, RLS policies missing.

## 16. LLM / AI features
- Prompt injection (direct and indirect via documents, web pages, emails, tool output), system prompt leakage.
- Tools/agents with excessive permissions, no human confirmation on destructive actions, SSRF/exfiltration via tool calls or rendered Markdown images/links.
- Model output rendered as HTML/executed as code/SQL without sanitisation.
- Secrets or other users' data included in prompts; cross-tenant leakage through shared context or vector stores.
- Missing spend limits/rate limits on paid model calls (cost abuse).
