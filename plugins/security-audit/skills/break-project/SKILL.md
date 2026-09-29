---
name: break-project
description: Full-project security audit in the style of a pentest. Hunts every class of vulnerability (secrets, auth/authz, injections, XSS/CSRF/SSRF, crypto, dependencies, config, Docker/CI, business logic, APIs, LLM features...) through static analysis plus safe local dynamic tests, then writes a detailed French Markdown report (description, impact, reproduction steps, fix) at the project root. Strictly read-only on the code - never edits, fixes or commits anything. Use this whenever the user types /break-project, /test-security or /review-project, or asks to audit, pentest, "break", attack, or test the security of a whole project or codebase, find all vulnerabilities/failles, or asks "is my project secure?" - even if they don't say "audit". For reviewing only the pending diff of a branch, the built-in security-review is the better fit.
---

# break-project - whole-project security audit (read-only)

You are acting as an attacker who has been given the source code. Your job is to find every exploitable weakness in the project, prove the ones you can, and write a report the developer can act on without needing to ask you anything. You never fix anything yourself: the developer decides what to change, and an audit that silently patches code destroys the evidence and can hide the very problems they need to see.

The report is in **French** (technical terms such as CVE, CWE, XSS, IDOR stay as-is).

## Ground rules (read these first, they override everything else)

1. **Do not modify the project.** No Edit/Write/sed -i on project files, no `npm audit fix`, `npm install`, `composer update`, `pip install` into the project, no migrations, no formatters, no `git commit/checkout/stash/reset/clean`. Dependency installs alter lockfiles and `node_modules`; that is a code change.
2. **Only two writes are allowed inside the project:**
   - the report file `SECURITY_AUDIT_<YYYY-MM-DD>.md` at the project root;
   - one line adding that report name to `.gitignore` (see "Finish" below).
3. **Scratch material goes outside the project** (the session scratchpad directory, or `mktemp -d`): PoC scripts, payload files, captured responses, tool output.
4. **Dynamic tests hit localhost only**, on a dev/disposable environment. Never send a request to a host you did not start yourself, never touch production, staging or third-party APIs. See `references/dynamic-testing.md` before running anything.
5. **Redact secrets in the report** (keep the first 4 characters and the type, e.g. `AKIA****(AWS access key)`). The report itself will be sensitive; leaking real credentials into it would create a new vulnerability.
6. **No denial-of-service.** Rate-limit checks are a handful of requests (about 20-30 at most), never load or fuzzing floods.
7. Sub-agents you spawn inherit these rules: say so explicitly in their prompt.

## Workflow

Track these phases with a todo list so none is skipped.

### 1. Reconnaissance
Understand what you are attacking before hunting: languages/frameworks (manifest files, lockfiles), entry points (routes, controllers, CLI, webhooks, queues, cron, WebSocket, GraphQL), trust boundaries (what comes from the user/network/third parties), authentication and session mechanism, data stores, secrets handling, deployment (Dockerfile, compose, k8s, Terraform, CI workflows), and where sensitive data lives. Note what is out of reach (e.g. code generated, vendored, or missing) so the report can state its limits. Write a short attack-surface map for yourself; it drives the rest.

### 2. Static audit
Work through `references/checklist.md`. It lists the vulnerability classes to consider and where to look for each. Skip classes that clearly don't apply to the stack (say so in the report's scope section), but don't skip a class merely because it's tedious.

For anything beyond a small project, parallelise: spawn several read-only sub-agents (e.g. one for auth/authz, one for injection and input handling, one for dependencies/secrets/config/CI, one for frontend) each with the ground rules above, the attack-surface map and a request for findings with `file:line` evidence. You remain responsible for verifying what they return.

Always include:
- **Secrets**, in the working tree *and* git history (`git log -p -S`, `git log --all --diff-filter=D`) - a secret deleted from HEAD is still leaked.
- **Dependencies**: known CVEs, unpinned/typosquat-looking packages, install scripts, abandoned packages.
- **Authorization on every route**, not just "is there a login" - most real breaches are missing ownership checks.

### 3. Read-only tooling
Use what's installed; check with `which`. Examples: `semgrep --config auto`, `gitleaks detect --no-git=false`, `trufflehog`, `npm audit --json`, `pip-audit`, `composer audit`, `bandit`, `gosec`, `cargo audit`, `trivy fs`, `hadolint`. Run them with output redirected to the scratchpad. If a tool needs installing, don't install it into the project; mention in the report that it could improve coverage. Scanner output is a lead, not a finding: verify each hit.

### 4. Dynamic tests (local)
Follow `references/dynamic-testing.md`. It covers how to check the environment is safe, start the app on localhost, prove suspected vulnerabilities with minimal requests, and shut everything down. If the app can't be started safely (needs prod credentials, remote DB, missing services), say so in the report and mark affected findings "probable" instead of "confirmed" - don't guess your way around it.

### 5. Verify before you report
False positives waste the developer's time and erode trust in the whole report. For each candidate:
- trace input source -> sink and look for existing mitigations (framework auto-escaping, ORM parameterisation, middleware, WAF/proxy config, validation upstream);
- assign a status: **Confirmé** (reproduced), **Probable** (code path is clearly exploitable but not run), **À vérifier** (plausible, depends on something you couldn't see);
- assign severity by real-world exploitability and impact, not by how scary the class sounds: Critique / Élevée / Moyenne / Faible / Info. Consider prerequisites (unauthenticated? needs admin? needs user interaction?).
Merge duplicates (one root cause = one finding, listing all locations).

### 6. Write the report
Use `references/report-template.md` for structure. Every finding needs: what it is, where (`file:line`), why it matters (concrete impact), how to reproduce (numbered steps a developer can copy - `curl` commands, payloads, expected vs. actual response), and how to fix (explain the fix and give a corrective snippet *inside the report*; do not apply it). Sort findings by severity. Include what is done well (so the developer knows what not to break) and what was not tested (so nobody reads "no finding" as "safe").

Reproduction steps must be safe to run by the developer on their own dev environment: no destructive payloads (use `SELECT`/sleep/`id`-style proofs, harmless marker files, `alert(document.domain)`), and say which environment they're for.

### 7. Finish
1. Stop any process you started (dev server, containers) and delete temp data you created. Confirm ports are free.
2. `.gitignore`: if the project is a git repository, append `SECURITY_AUDIT_*.md` if it isn't already covered (create `.gitignore` if the repo has none). If it isn't a git repo, skip and say so. The report describes how to attack the project, so it must not be committed by accident.
3. Check `git status` (if a repo) or file mtimes to confirm the only changes are the report and `.gitignore`. If anything else changed (e.g. a tool wrote a cache file into the project), tell the user exactly what.
4. Reply to the user in French, briefly: path of the report, count of findings per severity, the top 3 most urgent, anything you couldn't test, and a reminder that no code was modified. Don't paste the whole report into the chat.
