# brieuc-claude-toolkit

Marketplace de plugins Claude Code.

| Plugin | Description |
|---|---|
| [`security-audit`](#security-audit) | Audit de sécurité complet d'un projet, avec rapport détaillé. Ne modifie jamais le code. |
| [`pr`](#pr) | Analyse les commentaires de review de la PR de la branche et propose solution + réponse à copier-coller. |

## Installation

Dans Claude Code, ajouter la marketplace une fois :

```
/plugin marketplace add <URL ou org/repo de ce dépôt>
```

Puis installer les plugins voulus, par exemple :

```
/plugin install security-audit@brieuc-claude-toolkit
```

Redémarrer Claude Code après l'installation.

Pour récupérer les mises à jour :

```
/plugin marketplace update brieuc-claude-toolkit
```

---

## security-audit

Audit de sécurité complet d'un projet, façon pentest :

- analyse statique de tout le code (secrets, y compris dans l'historique git, authentification, autorisation, injections, XSS/CSRF/SSRF, crypto, dépendances, Docker/CI, logique métier, API, fonctionnalités LLM…) ;
- tests dynamiques **en local uniquement** et non destructifs, quand l'application peut être lancée sans toucher à des ressources réelles ;
- rapport `SECURITY_AUDIT_<date>.md` en français, à la racine du projet, avec pour chaque faille : sévérité, statut, emplacement, impact, étapes de reproduction et correction proposée.

**Le plugin ne modifie jamais le code.** Les seules écritures dans le projet sont le rapport et l'ajout de `SECURITY_AUDIT_*.md` au `.gitignore`, pour que le rapport (qui explique comment attaquer le projet) ne soit pas committé par erreur.

### Utilisation

Dans le projet à auditer :

```
/security-audit:break-project
```

Alias : `/security-audit:test-security`, `/security-audit:review-project`. On peut aussi simplement demander « fais un audit de sécurité du projet ».

Précisions utiles à ajouter à la commande, par exemple : `statique uniquement`, `seulement le dossier api/`, `l'app se lance avec docker compose up`.

---

## pr

Aide à traiter les commentaires de review de la PR de la branche courante :

- récupère via `gh` les fils de commentaires non résolus, les reviews et les commentaires généraux (en ignorant les fils résolus, ceux auxquels l'auteur a déjà répondu et le bruit des bots CI) ;
- vérifie chaque commentaire contre le code réel : fondé, partiellement fondé, non fondé, déjà corrigé ou question à discuter ;
- propose pour chacun **une solution**, **une courte explication** et **une réponse de une ou deux phrases**, sur un ton naturel, à copier-coller sur GitHub.

**Le plugin ne modifie jamais le code et ne publie rien sur GitHub** : c'est toi qui réponds. À la fin, il propose d'appliquer les corrections des commentaires fondés.

Prérequis : `gh` installé et authentifié (`gh auth status`).

### Utilisation

Dans le projet, sur la branche de la PR :

```
/pr:comments
```

On peut aussi passer un numéro ou une URL de PR (`/pr:comments 123`), ou simplement demander « regarde les commentaires de ma PR ».

---

## Développement

Structure :

```
.claude-plugin/marketplace.json     # liste des plugins de la marketplace
plugins/<nom-du-plugin>/
  .claude-plugin/plugin.json        # manifeste (incrémenter "version" à chaque release)
  skills/<nom-du-skill>/SKILL.md    # un dossier par skill
```

Ajouter un plugin : créer `plugins/<nom>/` sur ce modèle, puis l'ajouter au tableau `plugins` de `.claude-plugin/marketplace.json` et au tableau en haut de ce README.

Tester localement sans publier :

```
claude plugin validate .
claude --plugin-dir plugins/<nom-du-plugin>
```
