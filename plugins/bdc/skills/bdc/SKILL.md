---
name: bdc
description: Base de connaissance (Bdc) d'un projet, tirée des pièces d'un appel d'offres (CCTP, RC, CCAP, annexes PDF/Excel) et de notre réponse, versionnée dans le dépôt (dossier bdc/). À utiliser pour générer une Bdc, la mettre à jour (réponse du client, notes de réunion, nouvelle version d'une pièce, décision interne), répondre à une question sur le projet, ou en tirer un livrable (tickets, swagger/OpenAPI, schéma de base de données, doc lisible). Ex. « génère la Bdc à partir de ces fichiers », « le client a répondu à la Q-012 », « que dit le CCTP sur l'authentification ? », « génère le swagger depuis la Bdc ».
---

# Bdc : base de connaissance projet

La Bdc est la vue **structurée, sourcée et critique** des pièces d'un appel d'offres, écrite pour les développeurs. Les pièces font foi ; la Bdc permet de s'y retrouver sans les relire, de répondre de façon vérifiable, et de garder la trace de tout ce qui reste flou. Un appel d'offres = une Bdc = un projet, dans `bdc/` à la racine du dépôt git du projet. Tout est rédigé en français.

Dans ce skill, `<skill>` désigne le dossier de ce fichier (« Base directory for this skill »). Les formats de tous les fichiers sont dans [references/format.md](references/format.md) : lis-le avant d'écrire dans `bdc/`.

## Règles qui valent partout

1. **Rien sans source.** Tout fait porte au moins une ligne `Citation (<PIÈCE> p.<N>) : « … »` (ou `<PIÈCE> › <Onglet>!<Cellule>` pour un tableur), citation **exacte**, retrouvable dans `bdc/sources/<PIÈCE>.md`. La reformulation s'ajoute à la citation, elle ne la remplace jamais.
2. **Certitude affichée.** Chaque élément est `explicite` (écrit tel quel) ou `déduit` (avec le raisonnement en une ligne). Ce qui n'est ni écrit ni déductible devient une question dans `questions.md`, avec une hypothèse de travail clairement marquée.
3. **Les pièces font foi.** Si la Bdc et `bdc/sources/` divergent, corrige la Bdc et note-le dans `journal.md`. Une contradiction entre pièces se tranche par `ordre_des_pieces` de `config.yml` ; elle devient quand même une question dès qu'elle a un impact dev.
4. **IDs stables.** Un ID n'est jamais renuméroté ni réutilisé. Un élément retiré reste en place, marqué `[supprimé AAAA-MM-JJ : raison]`. Un élément qui change de périmètre garde son ID.
5. **Périmètre dev.** Les sujets listés dans `exclusions` de `config.yml` (par défaut : prix/BPU/DPGF, CV et profils, RSE/environnement, planning) sont écartés, et chaque section écartée est inscrite dans `hors-perimetre.md` avec sa raison. Ce qui touche le développement reste, même dans une pièce contractuelle : SLA, pénalités liées au service, sécurité, RGPD, accessibilité, réversibilité, recette, garantie, hébergement technique, reprise de données. Pas de planning ni d'estimation, sauf demande explicite.
6. **Toute écriture se termine par les deux contrôles**, à relancer jusqu'à zéro erreur :
   ```bash
   python3 <skill>/scripts/verifier_bdc.py bdc --maj   # structure + récapitulatifs
   python3 <skill>/scripts/verifier_citations.py bdc   # citations exactes, à la bonne page
   ```
7. **Le user committe.** Tu écris dans `bdc/` ; le commit reste à l'équipe, sauf demande explicite.

## Choisir la branche

Trouve la Bdc : `bdc/INDEX.md` à la racine git (`git rev-parse --show-toplevel`), sinon cherche `**/bdc/INDEX.md`.

| Demande | Branche |
|---|---|
| Générer une Bdc (pas de `bdc/`, ou régénération demandée explicitement) | Lis [references/generation.md](references/generation.md) et suis-le jusqu'au bout. |
| Réponse du client, notes de réunion, décision interne, nouvelle pièce ou nouvelle version d'une pièce, correction, merge de branches (IDs en double, conflits dans `bdc/`) | Lis [references/mise-a-jour.md](references/mise-a-jour.md). |
| Question sur le projet | **Consultation**, ci-dessous. |
| Comparer du code déjà développé à la Bdc, état de réalisation, conformité | Skill `existant` (`/existant`). |
| Tickets, swagger/OpenAPI, schéma de base de données, documentation lisible, liste de questions à envoyer au client, autre export | Lis [references/livrables.md](references/livrables.md). |

Si `bdc/` existe déjà et qu'on te demande de « générer », c'est une mise à jour (nouvelles pièces). Une régénération complète n'a lieu que sur demande explicite, et elle reprend les réponses de `questions.md` et tout `journal.md`.

## Consultation

1. Lis `bdc/INDEX.md`, puis seulement les fichiers que sa carte désigne pour la question. Pour un terme ou un ID, `grep -rn` dans `bdc/` va plus vite que la lecture.
2. Vérifie dans `bdc/sources/` chaque citation que tu vas donner (`grep -n` sur un morceau de la phrase).
3. Réponds : d'abord la réponse directe, puis les IDs et sources (pièce, §, page), en séparant l'explicite du déduit. Signale les questions ouvertes (`Q-…`) qui touchent la réponse et l'hypothèse de travail en vigueur.
4. Si la Bdc ne couvre pas le point, dis-le en ces termes, puis cherche dans `bdc/sources/` :
   - trouvé dans les pièces mais absent de la Bdc : c'est un trou de la Bdc ; donne la réponse sourcée et propose de l'ajouter (mise à jour) ;
   - absent des pièces : propose une nouvelle question pour le client.

La réponse est terminée quand chacune de ses affirmations porte une source ou la mention `déduit`.

## Lien avec le skill todo

Seulement si un skill `todo` figure dans la liste des skills de la session ; sinon, n'en parle pas.

À la fin d'une génération ou d'une mise à jour, propose en une liste numérotée :
- un **point de réunion** par question `bloquante` ou `majeure` nouvellement ouverte (texte : la question pour le client, raccourcie, suivie de `(Bdc Q-012)`) ;
- une **tâche** par action qui revient à l'équipe (fournir une pièce manquante, trancher une décision interne).

Attends le choix du user (tout, des numéros, rien). Crée ensuite les entrées retenues via le skill `todo`, sur le projet du dépôt, puis ajoute `- Todo : #<id>` à chaque question concernée dans `questions.md`.
