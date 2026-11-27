# Format de la Bdc

Source de vérité unique des formats. Tout est en Markdown (sauf `config.yml`), lisible par un humain sans outil.

## Arborescence

```
bdc/
  INDEX.md               seul fichier lu à chaque consultation : le projet en bref + carte des fichiers
  config.yml             paramètres : pièces, ordre des pièces, périmètres, domaines, modules, exclusions
  glossaire.md
  exigences/<domaine>.md               un seul périmètre
  exigences/<périmètre>/<domaine>.md   plusieurs périmètres (un dossier par périmètre)
  modele/entites.md      objets métier → schéma de base de données
  modele/acteurs.md      acteurs, rôles, matrice des droits
  modele/interfaces.md   échanges avec des systèmes externes, imports/exports
  modele/processus.md    enchaînements métier, statuts, workflows
  perimetres.md          seulement s'il y a plusieurs périmètres
  analyse.md             analyse critique transverse (modules activés)
  questions.md           toutes les questions et demandes de précision
  hors-perimetre.md      tout ce qui a été écarté, avec la raison
  couverture.md          chaque section de chaque pièce → ce qu'elle a produit
  journal.md             historique : générations, réponses intégrées, décisions, nouvelles versions
  sources/registre.md    les pièces : code, fichier, version, date, sha256, taille
  sources/<PIÈCE>.md     texte extrait de la pièce, avec repères de page ou de cellule
  sources/originaux/     fichiers d'origine (PDF, XLSX…)
  tickets/T-<NNN>.md     un fichier par ticket (tenus à jour, pas régénérés)
  existant.yml           code déjà développé à confronter à la Bdc (skill existant)
  existant.local.yml     chemins de ce code sur la machine : ignoré par git
  existant/<nom>.md      cartographie de chaque code existant (skill existant)
  realisation.md         état de réalisation de chaque exigence (skill existant)
  livrables/             exports générés (openapi, schéma, doc, questions…), régénérables
```

Un fichier qui n'a pas de contenu pour ce projet n'est pas créé (par exemple `modele/interfaces.md` sans interface externe), et la carte d'INDEX ne le mentionne pas.

## Récapitulatifs et contrôle de structure

Les chiffres d'INDEX (entre `<!-- chiffres -->` et `<!-- /chiffres -->`) et les tableaux récapitulatifs de `questions.md` et des fichiers d'exigences (entre `<!-- recap -->` et `<!-- /recap -->`) sont **écrits par le script**, jamais à la main :

```bash
python3 <skill>/scripts/verifier_bdc.py bdc --maj
```

Le script contrôle aussi la structure : conflits git, IDs en double ou cités sans être définis, IDs provisoires, champs obligatoires, valeurs autorisées, périmètres et domaines de `config.yml`, lignes de `couverture.md`. Les valeurs autorisées sont celles de ce fichier ; le script suit ce format à la lettre (`- Champ : valeur`, fiches en `### <ID> : <titre>`).

## Citations et sources

Une citation se trouve toujours sur sa propre ligne, sous cette forme exacte (le script `<skill>/scripts/verifier_citations.py` la vérifie) :

```
- Citation (CCTP §4.2.1 p.37) : « Le système doit permettre l'authentification des agents via le SSO de l'établissement. »
- Citation (ANX2 › Exigences!B14) : « Export CSV quotidien des dossiers clos »
```

- Le premier mot entre parenthèses est le **code de la pièce** (celui de `sources/registre.md`). `§` est facultatif, la page (`p.N`) obligatoire pour un PDF, la cellule pour un tableur.
- Le texte entre « » est copié de `sources/<PIÈCE>.md`, à l'espace près. Pour sauter un passage, utilise `[…]`. Pas de correction des fautes de la pièce ; ajoute `[sic]` après si besoin.
- Une citation reste courte : la phrase ou la ligne de tableau qui porte l'information, pas le paragraphe entier.
- Un élément tiré de plusieurs pièces a plusieurs lignes `Citation`.
- Un élément issu d'une réponse du client ou d'une décision interne a une ligne `- Source : Réponse client Q-012 (2026-12-03, mail de M. X)` ou `- Source : Décision interne (2026-12-03, réunion d'équipe)` à la place d'une citation de pièce.

## config.yml

```yaml
projet: Portail usagers XYZ          # nom lisible
todo_projet: portail-xyz             # section de la todo ; par défaut, le nom du dépôt git
public: dev
exclusions: [prix, BPU/DPGF, CV et profils, RSE et environnement, planning]
ordre_des_pieces: [AE, CCAP, CCTP, ANX1, MT]   # Citation (CCAP art. 4 p.6) — vide si non défini (et alors une question)
perimetres:                          # un seul élément si le projet n'a pas de découpage
  - id: socle
    nom: Back-office d'administration et API globale
    source: CCTP §1.3 p.5
  - id: front-rh
    nom: Front RH
    source: CCTP §6 p.80
domaines:                            # codes utilisés dans les IDs d'exigence
  AUTH: Authentification et comptes
  DOS: Gestion des dossiers
  SEC: Sécurité
modules: [ecarts-offre, mutualisation, impacts-socle, droits-croises]
```

## INDEX.md

```markdown
# Bdc : <projet>

> Générée le AAAA-MM-JJ, mise à jour le AAAA-MM-JJ. <!-- chiffres --><!-- /chiffres -->

## Le projet en bref
<30 lignes maximum : objet du marché, utilisateurs, grands blocs fonctionnels, contraintes techniques majeures, ce qui est hors marché. Chaque phrase renvoie à ses IDs.>

## Périmètres
<seulement s'il y en a plusieurs : id, nom, une ligne de description>

## Carte
| Fichier | Contenu | À lire pour |
|---|---|---|
| exigences/socle/AUTH.md | 14 exigences : SSO, comptes, mots de passe | questions de connexion, comptes, profils |

## Vocabulaire essentiel
<15 à 20 termes au plus, une ligne chacun ; le reste est dans glossaire.md>

## Domaines
<code → nom, pour décoder les IDs>
```

## Exigences : `EX-<DOMAINE>-<NNN>`

Numérotation par domaine, sur trois chiffres, jamais réutilisée. Les règles de gestion sont des exigences de type `règle de gestion`.

```markdown
### EX-AUTH-003 : Authentification des agents par SSO
- Périmètre : socle
- Type : fonctionnelle | règle de gestion | technique | sécurité | performance | exploitation | accessibilité | données | recette | contractuelle
- Nature : obligatoire | souhaitée | optionnelle | variante | PSE
- Certitude : explicite
- Citation (CCTP §4.2.1 p.37) : « Le système doit permettre l'authentification des agents via le SSO de l'établissement. »
- Notre réponse : engagé | partiel | non traité | engagement supplémentaire | sans offre
- Citation (MT §3.1 p.12) : « … »
- Liens : AC-Agent, IF-SSO, Q-004

<Reformulation pour un dev : ce qu'il faut construire, contraintes, seuils, unités, critère d'acceptation quand la pièce en donne un.>
```

- `Nature` reprend la modalité de la pièce : « doit », « devra », « est tenu de » → obligatoire ; « souhaite », « devrait » → souhaitée ; « pourra », « peut » → optionnelle.
- `Notre réponse` : `engagé` si notre offre le couvre (citation MT), `partiel` (dire ce qui manque), `non traité` (l'offre n'en parle pas), `engagement supplémentaire` (promis dans l'offre sans être demandé, source MT seule), `sans offre` si aucune offre n'a été fournie.
- Un fichier d'exigences commence par son titre, une ligne `<!-- recap -->` puis une ligne `<!-- /recap -->`, puis les fiches dans l'ordre des IDs.

## Modèle

### Entités : `EN-<NomMetier>` (PascalCase, nom du métier tel qu'il est dans les pièces)

```markdown
### EN-Dossier
- Périmètre : socle (utilisée par : front-rh, front-usager)
- Certitude : explicite
- Citation (CCTP §5.1 p.42) : « … »
- Définition : …
- Attributs : | nom | type pressenti | obligatoire | source ou déduit |
- Relations : EN-Usager (1..n), …
- Cycle de vie : PR-InstructionDossier (statuts : brouillon → déposé → instruit → clos)
- Volumétrie : … (source) ou inconnue → Q-…
- Conservation / RGPD : …
- Liens : EX-DOS-001, EX-DOS-004
```

### Acteurs : `AC-<Nom>`

Une fiche par acteur ou rôle (qui il est, combien, par quel canal il accède, citations), puis une **matrice des droits** `acteur × entité/action` (C, L, M, S, valider…) où chaque case non vide renvoie à sa source ou à `déduit`, et chaque case inconnue vaut `?` avec sa question.

### Interfaces : `IF-<Nom>`

Système externe, sens (entrant/sortant), déclencheur, fréquence, protocole, format, volumétrie, authentification, gestion d'erreur, environnement de test ; chaque champ sourcé ou `inconnu → Q-…`.

### Processus : `PR-<Nom>`

Déclencheur, acteurs, étapes numérotées, statuts et transitions, règles (renvoi aux `EX-…`), cas d'erreur, fin.

## Tickets : `T-<NNN>`, un fichier `tickets/T-<NNN>.md` par ticket

```markdown
### T-004 : Connexion par SSO des agents
- Statut : à faire | en cours | fait | obsolète (raison)
- Périmètre : socle
- Exigences : EX-AUTH-003, EX-AUTH-004
- Questions : Q-031 (bloquante)
- Dépend de : T-001
- GitLab :

## Contexte
<deux ou trois phrases>

## À faire
<ce qu'il faut construire ; si une partie existe déjà, seulement ce qui manque, avec l'emplacement du code existant>

## Critères d'acceptation
- [ ] <tiré des exigences : seuils, règles, cas d'erreur, avec l'ID entre parenthèses>
```

`GitLab` reste vide tant que le ticket n'est pas créé dans GitLab ; ensuite il contient son numéro (`#123`). Un ticket n'est jamais supprimé : il passe `obsolète` avec la raison.

## Glossaire

```markdown
### Dossier
- Définition : …
- Citation (CCTP §2 p.8) : « … »
- Aussi appelé : « demande » (ANX1), « requête » (MT) → Q-021 si le sens diffère
- Périmètre : tous | <périmètre>
```

Termes classés par ordre alphabétique. Les sigles ont une fiche avec leur développement.

## Questions : `Q-<NNN>`, dans un seul fichier `questions.md`

Le fichier commence par son titre, une ligne `<!-- recap -->` puis une ligne `<!-- /recap -->`, puis les fiches dans l'ordre des IDs.

```markdown
### Q-012 : Durée de conservation des dossiers clos
- Statut : ouverte | posée (AAAA-MM-JJ) | répondue (AAAA-MM-JJ) | sans objet (raison)
- Gravité : bloquante | majeure | mineure
- Type : contradiction | flou | manque | erreur | incohérence offre | risque
- Périmètre : socle
- Citation (CCTP §5.4 p.47) : « Les dossiers clos sont conservés 5 ans. »
- Citation (CCAP art. 12 p.15) : « … conservées pendant 10 ans … »
- Contexte : <ce qui pose problème, en clair, sans jargon inutile>
- Impact dev : <ce qui est bloqué ou risque d'être refait>
- Hypothèse de travail : <ce qu'on suppose en attendant ; « aucune » pour une question bloquante>
- Question pour le client : « <formulée pour être posée telle quelle, autonome, polie et précise> »
- Liens : EX-DOS-007, EN-Dossier
- Todo : #31
- Réponse (AAAA-MM-JJ, canal, auteur) : <réponse telle que reçue, puis ce qu'on en a modifié dans la Bdc>
```

Gravité :
- **bloquante** : empêche de structurer la Bdc ou de faire un choix d'architecture (découpage du projet, techno imposée floue, modèle central contradictoire) ;
- **majeure** : change ce qu'on construit dans un domaine, ou le coût d'un domaine ;
- **mineure** : précision locale, coquille, renvoi cassé sans impact.

## hors-perimetre.md

Tableau `pièce | section | pages | raison (exclusion de config.yml ou autre)`. Une section partiellement utile y figure aussi, avec ce qui a été gardé.

## couverture.md

Un tableau par pièce, une ligne par section (titre de plus bas niveau qui porte du contenu) :

`section | pages | statut | renvoi`

`statut` vaut toujours l'un de : `extrait` (renvoi = IDs produits), `hors périmètre` (renvoi = ligne de hors-perimetre.md), `contexte` (présentation générale résumée dans INDEX, sans exigence), `doublon` (renvoi = la section ou pièce qui dit la même chose). Aucune ligne vide.

Pour un tableur : une ligne par onglet, ou par bloc de lignes si l'onglet est long.

## analyse.md

Une section par module activé dans `config.yml`, chacune avec un résumé puis les constats, chaque constat renvoyant à des IDs et des `Q-…`. Modules connus :

- `ecarts-offre` : exigences `non traité` ou `partiel`, engagements supplémentaires, promesses de l'offre plus fortes que la demande ;
- `mutualisation` : besoins décrits séparément dans plusieurs périmètres qui devraient aller dans le socle ;
- `impacts-socle` : spécificités d'un périmètre qui imposent une évolution du socle ou contredisent une règle commune ;
- `droits-croises` : qui voit quoi d'un périmètre à l'autre, cloisonnement des données dans l'API commune.

Un module propre au projet peut être ajouté au cadrage (nom en kebab-case, une ligne d'objet en tête de section).

## perimetres.md

Une fiche par périmètre : nom, citation qui le définit, utilisateurs, ce qu'il apporte en plus du socle ou du squelette, fichiers d'exigences.

## journal.md

Entrées datées, la plus récente en haut :

```markdown
## 2026-12-03 : réponse du client à Q-012
- Qui : <user>, via mail du client du 2026-12-02
- Modifié : EX-DOS-007 (durée 10 ans), EN-Dossier (conservation)
- Ouvert : Q-045
```

## sources/registre.md

Tableau `code | fichier d'origine | intitulé | version/date de la pièce | sha256 | taille | extraction` ; `extraction` signale les problèmes (pages avec peu ou pas de texte, conversion depuis Word, mise en colonnes).

Codes de pièce : courts, en majuscules, stables (`RC`, `AE`, `CCAP`, `CCTP`, `ANX1`, `ANX2`, `MT` pour notre mémoire technique, `REP-Q` pour les réponses aux questions des candidats…).

Repères dans `sources/<PIÈCE>.md` (écrits par `scripts/extraire.py`) : `[[p.N]]` avant chaque page d'un PDF ; `[[onglet:Nom]]` avant chaque onglet d'un tableur, puis une ligne par rangée non vide, `12: A=… | C=…`.
