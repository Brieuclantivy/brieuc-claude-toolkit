# Livrables tirés de la Bdc

Un livrable est **dérivé** : la Bdc reste la source de vérité. Tout ce qu'il contient renvoie à des IDs de la Bdc. Ce qu'elle ne dit pas n'est pas inventé : c'est marqué `À préciser (Q-…)` ou, si aucune question n'existe encore, ça en crée une (via `mise-a-jour.md`).

## Règles communes

1. Lis `bdc/INDEX.md`, puis les fichiers utiles. Demande le périmètre si le projet en a plusieurs et que la demande ne le dit pas (socle seul, un front, tout).
2. Écris dans `bdc/livrables/<type>/` sauf si le user donne une autre destination (dossier du code, outil de tickets). En tête du livrable (ou dans un fichier `LISEZMOI.md` à côté, pour un format qui ne prend pas de commentaire) : date, périmètre, état de la Bdc (date de la dernière entrée de `journal.md`), liste des questions ouvertes qui le touchent.
3. Termine par un résumé au user : ce qui est généré, ce qui est incomplet et pourquoi (questions ouvertes), ce qui a été déduit.
4. Rien n'est publié en dehors du dépôt (création de tickets GitHub/Jira, envoi) sans accord explicite du user, après qu'il a vu le contenu.

## Tickets

Les tickets ne sont pas un export : ils vivent dans `bdc/tickets/`, un fichier par ticket, au format de `format.md` (« Tickets »), et sont tenus à jour (par ce skill et par le skill `existant`).

- Découpage par défaut : un ticket par fonctionnalité livrable par un dev en quelques jours, qui regroupe les exigences liées (un même processus ou un même écran). Les exigences transverses (sécurité, performance, accessibilité) deviennent des critères d'acceptation des tickets concernés, ou un ticket dédié quand elles demandent un travail propre (mise en place du SSO, journalisation).
- Si `bdc/realisation.md` existe, pars de lui : pas de ticket pour une exigence `conforme` ; pour une exigence `partiel` ou `non conforme`, le ticket ne décrit que ce qui manque, avec l'emplacement du code existant.
- S'il existe déjà des tickets, complète-les : une exigence déjà couverte par un ticket non `obsolète` n'en reçoit pas un autre. Les nouveaux tickets prennent les numéros suivants.
- Les tickets bloqués par une question `bloquante` ou `majeure` l'indiquent dans `Questions`.
- Contrôle : chaque exigence `obligatoire` du périmètre est couverte par un ticket ou est `conforme` dans `realisation.md` ; liste à part les exigences non couvertes et pourquoi.
- Pas de charge, d'estimation ni de planning, sauf demande.
- Création dans GitLab : seulement sur demande, après avoir montré la liste et obtenu l'accord ; puis remplis le champ `GitLab` de chaque ticket.

## Swagger / OpenAPI

- OpenAPI 3.1 en YAML. Sources : entités (schémas), processus et exigences (opérations), acteurs et matrice des droits (sécurité par opération), interfaces (API exposées aux systèmes externes).
- Chaque schéma et chaque opération porte `x-bdc: [EN-Dossier, EX-DOS-004]`. Les choix de conception non dictés par la Bdc (nommage des routes, pagination, format d'erreur) sont listés dans la description de l'API, comme conventions proposées.
- Champs dont le type ou l'obligation est inconnu : `description: "À préciser (Q-…)"`.
- Valide le fichier si un outil est disponible (`npx @redocly/cli lint`, ou au moins un parse YAML).

## Schéma de base de données

- Demande la cible si elle n'est pas évidente dans le dépôt : DDL SQL (quel SGBD), DBML, diagramme Mermaid `erDiagram`. Par défaut : Mermaid + DBML.
- Sources : entités, attributs, relations, cycles de vie (statuts), volumétries, durées de conservation, matrice des droits (cloisonnement par périmètre ou par organisation).
- Chaque table et chaque colonne non triviale renvoie à son ID en commentaire. Les tables purement techniques (jointures, journal d'audit) sont marquées `technique`.
- Liste à part les choix de modélisation déduits (cardinalité supposée, historisation) et les attributs inconnus.

## Documentation lisible

- Public : un humain qui découvre le projet (dev, chef de projet, client). Demande lequel si ce n'est pas clair, et adapte le niveau de détail et le vocabulaire.
- Structure proposée : présentation, utilisateurs et rôles, parcours principaux, fonctionnalités par périmètre, données, interfaces, exigences transverses, points en suspens (questions ouvertes reformulées). Pas de citations à chaque ligne : un renvoi discret aux IDs suffit.
- Format : Markdown dans `bdc/livrables/doc/` par défaut ; un autre format (page web, document Word) si le user le demande.

## Questions pour le client

Document à envoyer au client ou à projeter en réunion, tiré de `questions.md`.

- Par défaut : questions `ouverte`, toutes gravités. Le user peut filtrer (gravité, périmètre, thème, réunion à venir).
- **Jamais de contenu interne** : les questions de type `incohérence offre` et `risque` sont exclues, comme les champs `Impact dev`, `Todo`, les écarts avec notre offre et les noms de nos fichiers. En cas de doute sur une question, demande au user.
- Regroupe par thème (domaine ou périmètre), les bloquantes en tête de chaque thème. Pour chaque question : sa référence `Q-…` (pour suivre la réponse), le contexte en une ou deux phrases avec les pièces et pages citées, la question telle qu'elle est dans `Question pour le client`. Si une hypothèse de travail existe, propose-la sous la forme « Notre compréhension : … Pouvez-vous la confirmer ? ».
- Pendant la consultation (questions des candidats), respecte la date limite et la forme imposées par le RC ; rappelle-les au user.
- Format : Markdown dans `bdc/livrables/questions/AAAA-MM-JJ.md` par défaut ; Word ou PDF si le user le demande.
- Après l'envoi, sur confirmation du user : passe les questions envoyées en `posée (date)` et lance les contrôles.

## Autre livrable

Applique les règles communes : sources = IDs de la Bdc, trous = questions, rien d'inventé. Si le livrable vise un autre public que les devs (par exemple un questionnaire à scripter), la Bdc reste la source, et `config.yml` peut être ajusté (exclusions, public) après accord du user.
