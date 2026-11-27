# Mise à jour de la Bdc

Toute mise à jour suit le même schéma : comprendre ce qui arrive, trouver **tout** ce que ça touche, modifier, tracer. Lis `bdc/INDEX.md` et `bdc/config.yml` d'abord, et `<skill>/references/format.md` avant d'écrire.

## Identifier ce qui arrive

| Arrivée | Source à citer dans les éléments modifiés |
|---|---|
| Réponse du client à une ou plusieurs questions (mail, réunion, réponses aux questions des candidats) | `Source : Réponse client Q-012 (date, canal, auteur)`. Si la réponse est un document, c'est une nouvelle pièce : voir plus bas. |
| Notes de réunion | Sépare les réponses du client (comme ci-dessus), les décisions internes et les nouvelles questions. |
| Décision interne de l'équipe | `Source : Décision interne (date, qui)` |
| Nouvelle pièce, ou nouvelle version d'une pièce (DCE modificatif, avenant, annexe ajoutée, offre finale) | Citations dans la nouvelle pièce. |
| Correction signalée (citation fausse, oubli) | La pièce d'origine. |
| Nouvelle question d'un dev | `questions.md` seulement. |

Si la date, le canal ou l'auteur d'une réponse manquent, demande-les en une question : une réponse sans origine n'est pas fiable.

## Réponse, décision, correction

1. Retrouve les questions concernées. Pour une réponse sans numéro (« le client dit que les dossiers sont gardés 10 ans »), cherche la question par mots-clés ; s'il n'y en a pas, la réponse s'applique directement aux éléments touchés.
2. Remplis la ligne `Réponse` de chaque question et passe son statut à `répondue (date)`.
3. Trouve **tous** les éléments touchés : ceux de `Liens`, puis `grep -rn` dans `bdc/` sur les termes, entités et valeurs concernés (une durée, un rôle, un format se répètent souvent dans plusieurs fichiers).
4. Modifie chaque élément : nouvelle valeur, ligne `Source` ajoutée, `Certitude : explicite`. Ne supprime pas la citation d'origine ; ajoute dessous `- Remplacé par : Réponse client Q-012 (date)`. L'hypothèse de travail de la question disparaît partout où elle avait été reprise.
5. Si la réponse crée de nouveaux éléments (exigence, attribut, rôle), donne-leur des IDs à la suite de la numérotation existante.
6. Si la réponse soulève un nouveau point ou contredit autre chose, ouvre une nouvelle question.
7. Mets à jour la carte d'INDEX si un fichier a été ajouté ou a changé de contenu ; les récapitulatifs et les chiffres viennent de `verifier_bdc.py --maj`.
8. Ajoute l'entrée dans `journal.md` : ce qui est arrivé, éléments modifiés, questions ouvertes ou closes.

Terminé quand plus aucun fichier ne contient l'ancienne valeur (sauf sous une ligne `Remplacé par`), que `journal.md` a son entrée, et que les deux contrôles (règle 6 de SKILL.md) finissent sans erreur.

## Nouvelle pièce ou nouvelle version

1. Nouvelle version d'une pièce existante : garde son code ; avant d'écraser, copie l'ancienne extraction dans le dossier de travail (`mktemp -d`). Nouvelle pièce : nouveau code.
2. Copie l'original dans `sources/originaux/` (nouvelle version : même nom de fichier, suffixé de la date ou du numéro de version), extrais-le avec `<skill>/scripts/extraire.py`, contrôle l'extraction comme à l'étape 0 de `generation.md`, mets à jour le registre.
3. Nouvelle version : `diff` entre l'ancienne et la nouvelle extraction pour repérer les sections modifiées, ajoutées, supprimées. Lance `verifier_citations.py` : chaque citation qui ne se vérifie plus doit être revue (page décalée, texte modifié, passage supprimé).
4. Applique aux sections nouvelles ou modifiées les étapes 2 (extraction), 3 (vérification) et 4 (consolidation, dans les fichiers existants, à la suite des IDs existants) de `generation.md`. Un élément dont la source a disparu est marqué `[supprimé date : retiré de <CODE> v2]`.
5. Applique l'étape 5 (analyse critique) aux éléments touchés et à leurs voisins : une nouvelle version contredit souvent l'ancienne ou une autre pièce. Vérifie si des questions ouvertes trouvent leur réponse dans la nouvelle pièce.
6. Mets à jour `couverture.md`, `hors-perimetre.md`, INDEX et `journal.md`, puis lance les contrôles finaux de l'étape 6 de `generation.md`.

## Après un merge de branches

Chacun crée ses IDs sur sa branche sans se coordonner ; les doublons se règlent ici.

1. Conflits git dans `bdc/` : dans les blocs `<!-- recap -->` et `<!-- chiffres -->`, garde n'importe quel côté (le script les réécrit) ; ailleurs, fusionne les deux côtés à la main, en gardant toutes les fiches.
2. Lance `verifier_bdc.py bdc`. Pour chaque ID `défini plusieurs fois` :
   - garde l'ID sur la fiche qui existait déjà sur la branche cible (`git log` / `git diff <base-du-merge>..<branche-fusionnée> -- bdc/` montre ce qui vient de la branche fusionnée) ;
   - exception : si la question de la branche fusionnée a déjà été envoyée au client (`Statut : posée`) et pas l'autre, c'est elle qui garde le numéro ;
   - donne à l'autre fiche le prochain numéro libre de sa série, et remplace l'ancien ID **uniquement dans les lignes apportées par la même branche** (même `git diff`) ;
   - signale les entrées todo qui citent l'ancien numéro (`Bdc Q-…`) et propose de les corriger ;
   - note chaque renumérotation dans `journal.md` (`Q-045 de la branche X → Q-052`).
3. Relance les deux contrôles jusqu'à zéro erreur.

## Fin de la mise à jour

Résume au user en quelques lignes : ce qui a changé (IDs), les questions closes et ouvertes. Fais ensuite la proposition todo (voir SKILL.md) pour les nouvelles questions, et propose de cocher dans la todo les entrées des questions closes (ligne `Todo : #…`).
