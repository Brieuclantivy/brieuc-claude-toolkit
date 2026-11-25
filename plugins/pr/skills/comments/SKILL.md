---
name: comments
description: Fetches the GitHub review comments on the pull request of the current branch, checks whether each one is valid against the actual code, works out a fix, and presents for every comment a proposed solution, a short explanation and a ready-to-paste natural reply. Read-only - never edits code and never posts anything on GitHub. Use whenever the user types /pr:comments, or asks to look at, handle, answer or go through the comments/remarks/review of their PR, e.g. "regarde les commentaires de la PR", "qu'est-ce qu'ils ont dit sur ma PR", "aide-moi à répondre à la review".
---

# comments - triage and answer the review comments of the current PR

The user wants to answer their reviewers themselves. Your job is to do the thinking: gather every open comment, check it against the real code, find the fix, and hand back something they can act on and paste in a few seconds.

Everything you write to the user is in **French**. The reply to paste is in the **language of the comment it answers** (usually French).

## Ground rules

1. **Read-only.** Do not edit, commit, push or format anything. Do not post, reply to, react to or resolve anything on GitHub (`gh pr comment`, `gh pr review`, `gh api -X POST/PATCH/PUT/DELETE` are all forbidden). The user replies themselves.
2. Only read through `gh` and local files/git. If `gh` is missing or not authenticated, say so and stop.
3. Never claim a comment is wrong without having read the code it targets.

## 1. Find the PR

```bash
gh pr view --json number,url,title,author,headRefName,baseRefName,headRefOid
```

- If there is no PR for the current branch, say so and stop. If the user gave a PR number or URL as argument, use it (`gh pr view <arg> ...`).
- Take `owner/repo` and the number from the PR `url` (this handles forks correctly).
- Compare `headRefOid` with `git rev-parse HEAD`. If they differ, warn the user that the local checkout is not the PR head (unpushed commits or out of date), because the code you read may not be the code that was commented on.

## 2. Fetch every comment

One GraphQL call gives inline threads with their resolved/outdated state, review bodies and general conversation comments:

```bash
gh api graphql -F owner=OWNER -F repo=REPO -F number=N -f query='
query($owner:String!, $repo:String!, $number:Int!) {
  repository(owner:$owner, name:$repo) {
    pullRequest(number:$number) {
      reviewThreads(first:100) { nodes {
        isResolved isOutdated path line originalLine startLine
        comments(first:50) { nodes { author { login } body url createdAt diffHunk } }
      } }
      reviews(first:100) { nodes { author { login } state body url submittedAt } }
      comments(first:100) { nodes { author { login } body url createdAt } }
    }
  }
}'
```

If a list returns 100 items, paginate (add `pageInfo { hasNextPage endCursor }` and `after:`).

Keep:
- **review threads that are not resolved** (one item per thread; later comments in the thread are part of its context);
- **review bodies** that are not empty and say something actionable;
- **conversation comments** from humans or review bots (Copilot, CodeRabbit, Qodo, Sonar...) that ask or suggest something.

Skip, and count them in the summary:
- resolved threads;
- threads whose **last** comment is from the PR author (already answered) - unless the reviewer replied after;
- pure noise: CI/coverage/deploy/changeset bots, "LGTM", approvals without text, comments from the PR author themselves.

If nothing is left, say so in one line and stop.

## 3. Analyse each comment

For each kept item:

1. **Read the code it targets** in the current working tree: the file at `path`, around `line` (or `originalLine` if `line` is null), with enough surrounding context to understand it - follow callers/callees when the comment is about behaviour. Use `diffHunk` to see what the reviewer saw. If the thread is outdated, check whether the code has since changed in a way that already addresses it.
2. **Judge validity**, one of:
   - ✅ **Fondé** - the reviewer is right;
   - 🟡 **Partiellement fondé** - right in part, or right in principle but the suggested fix is not the best one;
   - ❌ **Non fondé** - the reviewer missed something (show what: the line, the guard, the test that covers it);
   - ✔️ **Déjà corrigé** - the current code already addresses it;
   - ❓ **Question / à discuter** - a question, a matter of taste, or a decision that belongs to the user or the team.
   Base the judgement on evidence from the code, the project's conventions (CLAUDE.md, lint config, neighbouring code) and, when it matters, by running a quick read-only check (grep, type-check, existing tests). Do not modify anything to test.
3. **Find the solution**: the concrete change to make (a short diff or code snippet with `file:line`), or "rien à changer" with the reason. Keep it minimal and in the style of the surrounding code. If a reviewer's suggestion block (```suggestion) is correct, say so instead of rewriting it.
4. **Write the reply** the user will paste: 1 to 2 sentences, natural and friendly, like a colleague writing on GitHub - no "Great catch!", no bullet points, no over-politeness, no AI tone. Examples of the register:
   - fondé: « Bien vu, je corrige. » / « Exact, j'ajoute le check sur `null`. »
   - non fondé: « Normalement c'est couvert par le guard l.42 qui filtre les ids vides, donc on ne peut pas arriver ici avec `undefined`. »
   - déjà corrigé: « C'est réglé dans le dernier commit. »
   - question: « Je l'ai mis là pour éviter de recharger la config à chaque appel, mais je peux le déplacer si tu préfères. »
   Mention code with backticks, never paste long code in the reply.

When there are many comments (more than ~8) on different files, you may split the analysis across sub-agents (one per file or group of threads). Tell them explicitly that they are read-only and must not touch GitHub, and give them the comment text, `path`, line and `diffHunk`.

## 4. Present the result

Start with one line: PR number + title + link, then counts (`N commentaires à traiter, M ignorés (résolus / déjà répondus / bots)`).

Then one block per comment, in file order (general comments last):

~~~markdown
### 1. `src/foo.ts:42` — @reviewer ✅ Fondé
> Quoted comment (shortened to the essential if long)
[lien](url)

**Solution** : what to change, with a short diff/snippet if useful.

**Explication** : 1-3 sentences on why the comment is (or isn't) valid.

**Réponse** :
```text
Bien vu, je corrige.
```
~~~

Put each reply in its own ```text block so it can be copied in one click.

End with one line offering to apply the fixes of the valid comments (the user decides; do not apply anything without their go).
