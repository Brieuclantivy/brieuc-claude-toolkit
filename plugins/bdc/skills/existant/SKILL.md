---
name: existant
description: Confronte du code déjà développé (template, modules existants, dépôts locaux) à la Bdc du projet (dossier bdc/) - état de réalisation de chaque exigence (conforme, partiel, non conforme, à faire), matrice de conformité, mise à jour des tickets et des questions. À utiliser quand une partie du projet existe déjà ou a avancé, ex. « vérifie l'existant par rapport à la Bdc », « on a déjà un template avec connexion et OTP, lie-le à la Bdc », « mets à jour l'état de réalisation », « où en est la conformité ? ».
---

# existant : le code face à la Bdc

La Bdc (skill `bdc`) décrit le besoin. Ce skill dit **ce qui en est déjà réalisé** dans le code, avec preuves, et en tire les tickets et les questions. On le relance aussi souvent qu'on veut : l'état de réalisation se recalcule, il ne s'entretient pas à la main.

Dans ce skill, `<skill>` désigne le dossier de ce fichier, et `<bdc-skill>` le dossier voisin `<skill>/../bdc`. Les règles du skill `bdc` s'appliquent (lis `<bdc-skill>/SKILL.md`, section « Règles qui valent partout »), ainsi que ses formats (`<bdc-skill>/references/format.md`, notamment « Tickets » et « Questions »). Tout est rédigé en français.

**Règle propre à ce skill : le code ne modifie jamais une exigence.** Un écart entre le code et la Bdc devient un état, un ticket ou une question. Les pièces font foi, le code montre seulement où on en est.

## Prérequis

- Une Bdc : `bdc/INDEX.md` à la racine git du projet. Sans Bdc, dis-le et propose de la générer d'abord (`/bdc`).
- Les codes existants, déclarés dans deux fichiers :

```yaml
# bdc/existant.yml (commité : partagé par l'équipe)
sources:
  - nom: template                       # court, sans espace ; sert dans les renvois au code
    description: Template socle (connexion, OTP, profil)
    depot: git@gitlab.example.fr:equipe/template.git   # pour que chacun sache de quoi on parle
    perimetres: [socle]                 # périmètres de la Bdc concernés ; [tous] si un seul périmètre
```

```yaml
# bdc/existant.local.yml (ignoré par git : propre à chaque machine)
template: /home/moi/Projets/template
```

Si l'un manque, ou si un code n'a pas de chemin local, demande au user le nom, la description, le dépôt, les périmètres et le chemin, puis écris les fichiers. Vérifie que `bdc/existant.local.yml` est dans le `.gitignore` du projet ; sinon, ajoute-le et dis-le. Un chemin qui n'existe pas sur la machine : demande le bon.

## 1. Relever les versions

Pour chaque code : `git -C <chemin> rev-parse --short HEAD`, la branche, et `git -C <chemin> status --porcelain`. Des modifications non commitées sont analysées telles quelles, mais signale-le au user et dans l'en-tête de `realisation.md`. Un code hors git : note la date de dernière modification à la place du commit.

## 2. Cartographier le code

Un sous-agent par code (en parallèle), avec cette consigne, complétée des chemins absolus :

> Tu cartographies le code de `<chemin>` (nom : `<nom>`, description : <description>) pour le comparer ensuite à une base de connaissance. Lis le code, pas seulement la doc ni les noms de fichiers. Écris `<projet>/bdc/existant/<nom>.md` avec, en tête, `> Commit <hash> (<branche>), cartographié le <date>`, puis ces sections, chaque élément avec son emplacement `<nom>:<chemin relatif>:<ligne>` :
> - **Architecture** : langages, frameworks, organisation des dossiers, points d'entrée.
> - **Fonctionnalités** : ce que le code fait réellement, du point de vue d'un utilisateur, y compris les cas d'erreur traités.
> - **Modèle de données** : tables ou modèles, champs, types, contraintes, relations.
> - **API** : chaque route (méthode, chemin, rôle requis, entrée, sortie).
> - **Rôles et droits** : rôles existants, et qui peut faire quoi.
> - **Sécurité** : authentification, OTP, sessions, mots de passe, journalisation, chiffrement.
> - **Conventions** : nommage, format des erreurs, pagination, tests, configuration.
> - **Inachevé** : TODO, code mort, fonctionnalités à moitié faites, tests en échec ou absents.
>
> Décris ce qui est, sans juger. Ton message final : le chemin du fichier et une ligne de résumé.

Si `existant/<nom>.md` existait déjà et que le commit n'a pas changé, garde-le sans relancer le sous-agent.

## 3. Confronter

Un sous-agent par domaine d'exigences des périmètres concernés (en parallèle) :

> Tu évalues l'état de réalisation des exigences de `<projet>/bdc/exigences/<…>/<DOMAINE>.md` dans le code existant. Cartographies : `<projet>/bdc/existant/*.md` ; code : <noms et chemins>. Format des exigences : `<bdc-skill>/references/format.md`.
>
> Pour **chaque** exigence non supprimée, cherche dans le code (pas seulement dans la cartographie) ce qui la réalise, puis donne un état :
> - `conforme` : tout ce que dit l'exigence est réalisé, seuils et cas d'erreur compris ;
> - `partiel` : une partie est réalisée ; dis précisément ce qui manque ;
> - `non conforme` : le code fait autre chose que ce qui est demandé (exemple : OTP par SMS quand l'exigence demande une application) ;
> - `à faire` : rien n'existe ;
> - `non vérifiable` : ne peut pas se voir dans le code (performance, hébergement, organisation) ; dis comment le vérifier.
>
> Chaque état autre que `à faire` cite sa preuve : `<nom>:<chemin>:<lignes>` et ce que fait ce code, en une ligne. Écris dans `<TRAVAIL>/<DOMAINE>.md` un tableau `exigence | état | preuve | manque` puis, à part, la liste des **écarts qui demandent un choix** (le code fait autrement, et la décision revient au client ou à l'équipe), chacun avec les deux versions citées. Ton message final : le chemin et le nombre d'exigences par état.

`TRAVAIL=$(mktemp -d)`, hors du dépôt, supprimé à la fin.

Puis un sous-agent supplémentaire, sur l'ensemble des cartographies et de la Bdc : liste **ce que le code fait sans qu'aucune exigence ne le demande** (fonctionnalités, données collectées, rôles, routes), avec emplacement, et signale ce qui pose question (données personnelles, sécurité, droits trop larges, fonctionnalité contraire à une exigence).

## 4. Contre-vérifier

Pour chaque domaine, un **autre** sous-agent reprend toutes les exigences déclarées `conforme` ou `partiel` : il part du principe que le verdict est trop généreux, relit l'exigence (citation comprise) et le code cité, et corrige l'état et le manque si besoin, dans le même fichier de travail. `conforme` n'est accordé que si chaque élément de l'exigence a sa preuve.

Terminé quand chaque domaine a été contre-vérifié.

## 5. Écrire realisation.md

`bdc/realisation.md` est entièrement réécrit à chaque passage. Avant, garde une copie de l'ancien dans le dossier de travail pour la comparaison.

```markdown
# Réalisation

> État au AAAA-MM-JJ. template @ a1b2c3d (main) ; front @ 9f8e7d6 (develop, 3 fichiers modifiés non commités).

## Synthèse
| périmètre | domaine | conforme | partiel | non conforme | à faire | non vérifiable |

## Évolution depuis le AAAA-MM-JJ
<exigences qui ont changé d'état, régressions en premier ; « premier passage » sinon>

## <périmètre> : <domaine>
| exigence | état | preuve | manque | tickets | questions |
| EX-AUTH-003 | partiel | template:src/auth/sso.ts:12-48 : SSO OIDC agents | déconnexion SSO non gérée | T-004 | |

## Hors exigences
| code | emplacement | ce que ça fait | remarque |
```

Ce fichier est la **matrice de conformité** du projet : pour la recette, l'exporter tel quel ou en livrable (`<bdc-skill>/references/livrables.md`).

## 6. Questions

Pour chaque écart qui demande un choix et pour chaque élément « hors exigences » qui pose question :
- si la décision revient au **client** : une question au format de la Bdc (type `flou`, `contradiction` ou `risque`), avec la citation de l'exigence, la preuve dans le code, et une question qui propose les options (« Le template fait X. Le CCTP demande Y. Acceptez-vous X, ou faut-il Y ? ») ;
- si elle revient à l'**équipe** : une tâche dans la proposition todo (voir « Lien avec le skill todo » dans `<bdc-skill>/SKILL.md`), pas une question.

Suis `<bdc-skill>/references/mise-a-jour.md` pour les écrire (IDs, journal). Une question ouverte que le code règle de fait reste ouverte : le code ne répond pas à la place du client ; ajoute seulement le constat dans son contexte.

## 7. Tickets

Dans `bdc/tickets/` (format « Tickets » de `format.md`) :

- ticket dont toutes les exigences sont `conforme` → `Statut : fait` ;
- ticket dont une partie est réalisée → réécris `À faire` pour ne garder que ce qui manque, avec l'emplacement du code existant, et coche les critères d'acceptation déjà remplis ;
- exigence `partiel`, `non conforme` ou `à faire` couverte par aucun ticket actif → nouveau ticket, en suivant les règles de découpage de `livrables.md` ;
- ticket `fait` dont une exigence a régressé → `Statut : à faire`, et la régression dans `À faire` ;
- ticket qui n'a plus de raison d'être → `obsolète (raison)`.

Remplis les colonnes `tickets` et `questions` de `realisation.md`. Pas de charge ni de planning. Rien n'est envoyé dans GitLab sans demande explicite du user.

## 8. Contrôles et rapport

1. Ajoute `realisation.md`, `existant/` et `tickets/` à la carte de `bdc/INDEX.md` s'ils n'y sont pas (« À lire pour : est-ce déjà fait, où dans le code »).
2. Ajoute l'entrée dans `bdc/journal.md` : codes et commits analysés, chiffres par état, tickets et questions créés ou modifiés.
3. Lance les deux contrôles du skill `bdc` (règle 6 de `<bdc-skill>/SKILL.md`) jusqu'à zéro erreur.
4. Supprime le dossier de travail.
5. Rapport au user, court : chiffres par état, régressions, les écarts les plus importants en une ligne chacun, tickets créés, faits ou modifiés, nouvelles questions ; puis la proposition todo.
