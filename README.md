# brieuc-claude-toolkit

Marketplace de plugins Claude Code.

| Plugin | Description |
|---|---|
| [`security-audit`](#security-audit) | Audit de sécurité complet d'un projet, avec rapport détaillé. Ne modifie jamais le code. |
| [`pr`](#pr) | Analyse les commentaires de review de la PR de la branche et propose solution + réponse à copier-coller. |
| [`bdc`](#bdc) | Base de connaissance pour les devs, générée à partir d'un appel d'offres et de notre réponse. |

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

## bdc

Construit et entretient la **base de connaissance (Bdc)** d'un projet à partir des pièces d'un appel d'offres (CCTP, RC, CCAP, annexes PDF ou Excel) et de notre réponse. Elle est écrite pour les devs et versionnée dans le dépôt du projet, dans `bdc/` :

- **exigences** par domaine (et par périmètre si le projet a un socle commun et des applications spécifiques), chacune avec sa citation exacte, sa page, sa nature (obligatoire, optionnelle…) et ce que notre offre en dit ;
- **modèle** : entités, acteurs et matrice des droits, interfaces, processus ; **glossaire** ;
- **questions** au client dans `questions.md` : contradictions, flous, manques, erreurs, avec citations, impact dev, hypothèse de travail et question prête à poser ;
- **couverture** : chaque section de chaque pièce est rattachée à ce qu'elle a produit, ou écartée avec sa raison (prix, CV, RSE, planning…).

La génération privilégie l'exhaustivité au coût : extraction par lots en parallèle, vérification de chaque lot par un autre agent, analyse critique, puis contrôles automatiques de toutes les citations (`scripts/verifier_citations.py`) et de la structure (`scripts/verifier_bdc.py` : IDs, liens, champs, couverture, récapitulatifs).

Plusieurs branches peuvent modifier la Bdc en parallèle : les IDs en double sont détectés au merge et renumérotés par le skill, et les tableaux récapitulatifs se régénèrent au lieu de se fusionner à la main. Elle s'arrête après le cadrage pour faire valider la structure, et immédiatement si un point bloquant (découpage du projet flou, pièce manquante) l'empêche de partir dans la bonne direction.

Avec le skill `todo` installé, propose de créer les points de réunion et les tâches correspondant aux nouvelles questions.

Prérequis : `python3`, `pdftotext` (poppler-utils) ; LibreOffice seulement pour les pièces Word, ODT, XLS ou ODS.

### Code existant : `/existant`

Quand une partie du projet est déjà développée (un template avec connexion, OTP, profil…), `/existant` confronte ce code à la Bdc :

- déclare les codes dans `bdc/existant.yml` (commité : nom, description, dépôt, périmètres) et leur chemin local dans `bdc/existant.local.yml` (ignoré par git) ; le skill les demande s'ils manquent ;
- cartographie chaque code, puis donne à chaque exigence un état (`conforme`, `partiel`, `non conforme`, `à faire`, `non vérifiable`) avec la preuve dans le code ; chaque `conforme` est contre-vérifié par un autre agent ;
- écrit `bdc/realisation.md` (la matrice de conformité, avec l'évolution depuis le passage précédent) ;
- met à jour les tickets de `bdc/tickets/` (faits, réduits à ce qui manque, nouveaux) et crée les questions pour les écarts que le client doit trancher.

Le code ne modifie jamais une exigence : un écart devient un état, un ticket ou une question. À relancer quand le code avance.

### Utilisation

Dans le dépôt du projet, avec `/bdc` (ou `/bdc:bdc` si une autre commande `/bdc` existe), ou simplement en langage naturel :

```
génère la Bdc à partir de docs/ao/*.pdf et de notre mémoire technique docs/ao/MT.pdf
le client a répondu à la Q-012 : les dossiers sont conservés 10 ans (mail de Mme X du 03/12)
voici le DCE modificatif : docs/ao/CCTP_v2.pdf
que dit le CCTP sur l'authentification ?
génère le swagger du socle depuis la Bdc
/existant
prépare la liste des questions bloquantes et majeures pour la réunion client
```

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
