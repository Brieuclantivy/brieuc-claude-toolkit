# Dynamic testing protocol (local only, non-destructive)

Dynamic tests turn "this looks exploitable" into "here is the exact request and the response that proves it". They also carry risk: running an app can write to databases, send emails, call paid APIs. Follow these steps in order.

## 1. Decide whether it's safe to run
Read `.env*`, config files, docker-compose and the app's startup code, then answer:
- Does the DB / cache / queue / storage point to localhost or a container you can start? Or to a remote host, managed service, or something that looks like staging/production (cloud hostnames, `prod`, real domains)?
- Are there live third-party keys (payment, email/SMS, cloud, LLM) that a test request could trigger?
- Are there background jobs/cron that would fire on startup and act on real data?

If any answer is "remote/live": **do not start the app with that config.** Options: use a local DB (docker) with seed data if the project provides it, override the variables via environment for the process only (never edit the `.env`), stub the third party, or skip dynamic testing for the affected areas and mark findings "Probable". When it's ambiguous, ask the user once, with the concrete concern (e.g. "`DATABASE_URL` points to `db.xxx.supabase.co`, is that a throwaway dev DB?").

The user has opted into dynamic tests in principle, but that consent doesn't cover touching shared or real resources.

## 2. Start the app without changing the project
- Prefer the project's documented dev command (`npm run dev`, `php bin/cake.php server`, `docker compose up`...). Run in background with output redirected to the scratchpad. Bind to `127.0.0.1`.
- Don't run installs or migrations in the project. If dependencies are missing and the app can't start, don't fix it: note it and continue with static analysis. (If the user tells you a copy/worktree is fine to install into, work in a copy under the scratchpad.)
- Note the PID/container names so you can stop them at the end.
- If a tool would write into the project (build output, caches, sqlite files), prefer running against a copy of the project in the scratchpad (`cp -r` excluding `.git`/`node_modules` if cheap, or `git worktree` is NOT allowed since it modifies `.git`).

## 3. Test what you suspected
Use `curl`, small Python/Node scripts in the scratchpad, or a headless browser if available. Prove each suspected issue with the smallest request that shows it:
- **Authz / IDOR**: create two test users (or use seed data); with user A's session request user B's object; compare status and body. Try unauthenticated access to every sensitive route you found.
- **Injection**: harmless proofs - a quote that produces a SQL error, `SLEEP(2)`/`pg_sleep(2)` timing difference, `{{7*7}}` -> `49`, `$(id)`-style only if clearly a command sink and the environment is disposable.
- **XSS**: `<script>alert(document.domain)</script>` or an `img onerror` marker; confirm it's reflected unescaped in the response HTML/DOM.
- **CSRF / CORS / headers**: inspect response headers, send a cross-origin `Origin` and read `Access-Control-*`.
- **Auth**: token/JWT tampering, expired/none-alg tokens, session behaviour after logout, password-reset token predictability (on local data only).
- **Rate limiting**: 20-30 rapid requests to a login endpoint - enough to see whether any throttling exists, not enough to stress the server.
- **Info exposure**: request `/.env`, `/.git/HEAD`, `/actuator`, `/swagger`, `/graphql` introspection, verbose error pages.
- **Upload / traversal / SSRF**: benign markers only (a text file named `../marker.txt` in a scratch dir, SSRF to a listener you started on localhost).

Record for each test: exact command, request, response excerpt (redacted), and what it proves. These become the "Reproduction" and "Preuve" sections of the report.

## 4. Limits
- Localhost only. No scanning of networks, no requests to hosts you didn't start.
- No destructive payloads: no `DROP`, `DELETE`, `rm`, fork bombs, reverse shells, real data exfiltration, no persistence.
- No brute force beyond the small rate-limit probe; no fuzzing floods; no load testing.
- Data you create (test users, rows, files) should be cleaned up if it's on anything other than a throwaway DB; if it can't be cleaned, tell the user in the report.
- Stop if something behaves unexpectedly (e.g. an email actually gets sent, a remote host receives traffic) and tell the user.

## 5. Shut down
Kill the processes/containers you started, verify the ports are free (`ss -ltnp`), remove scratch data containing secrets or session cookies.
