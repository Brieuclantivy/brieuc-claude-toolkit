# Génération d'une Bdc

Objectif : une Bdc **complète du premier coup**, qu'on n'a pas à corriger ensuite. Le temps et les tokens ne comptent pas ; l'exhaustivité et l'exactitude, si. Dès qu'une pièce dépasse quelques pages, le travail lourd est confié à des sous-agents (outil Agent), lancés en parallèle par vagues d'environ 8 (tous les appels d'une vague dans un même message). Ton propre contexte sert à coordonner : tu lis les résumés et les fichiers de travail utiles, jamais toutes les pièces d'un coup.

Les sous-agents ne voient pas cette conversation. Chaque consigne de sous-agent ci-dessous est à compléter avec les chemins absolus (pièce, pages, `<skill>/references/format.md`, `bdc/config.yml`, dossier de travail) et à envoyer telle quelle.

Dossier de travail : `TRAVAIL=$(mktemp -d)`, hors du dépôt. Il contient les fichiers intermédiaires des sous-agents et disparaît à la fin.

## 0. Préparation

1. Les pièces : celles données par le user (chemins, dossier). S'il n'en a donné aucune, demande-les. Demande aussi si notre réponse (mémoire technique, annexes techniques de l'offre) fait partie du lot, si ce n'est pas évident.
2. Racine : `bdc/` à la racine git du projet. Hors dépôt git, demande où la créer.
3. Pour chaque pièce : attribue un code (voir `format.md`, « sources/registre.md »), copie l'original dans `bdc/sources/originaux/`, puis :

   ```bash
   python3 <skill>/scripts/extraire.py <original> <CODE> bdc/sources/<CODE>.md
   ```

   Le script gère PDF et XLSX directement, Word/ODT/XLS/ODS via LibreOffice. Il affiche le sha256, la taille et les pages avec peu ou pas de texte.
4. Contrôle chaque extraction :
   - pages avec peu ou pas de texte : regarde la page (outil Read sur le PDF, paramètre `pages`). Si c'est une page de garde ou blanche, note-le ; si c'est un scan ou un schéma porteur d'information, lis-la toi-même en image et ajoute sa transcription dans `sources/<CODE>.md` sous son repère, préfixée `[transcription de l'image]` ;
   - mise en page en colonnes ou tableaux éclatés : compare quelques pages au PDF ; si le texte est mélangé, signale-le dans le registre et relis ces pages en image lors de l'extraction ;
   - pièces citées mais non fournies (« cf. annexe 4 ») : note-les pour le cadrage.
5. Écris `sources/registre.md`.

Terminé quand chaque pièce a son `sources/<CODE>.md`, une ligne dans le registre et ses problèmes d'extraction notés.

## 1. Cadrage : ne pas partir dans une mauvaise direction

Tu fais cette étape toi-même, sans sous-agent : elle décide de toute la structure.

1. Lis le sommaire et les premières pages de chaque pièce, le RC en entier (objet, lots, contenu du dossier), l'article du CCAP qui fixe l'ordre de priorité des pièces, et les sections du CCTP qui décrivent le contexte, l'architecture cible et le découpage.
2. Détermine et note avec citations :
   - l'objet du marché, les utilisateurs, les grands blocs fonctionnels ;
   - la **forme du projet** : un seul périmètre, ou un découpage (lots, socle commun + applications spécifiques, modules…). Un découpage doit être **explicite dans les pièces** ;
   - les **périmètres** et leur définition sourcée ;
   - les **domaines** (codes de 2 à 5 lettres) qui découperont les exigences : assez fins pour qu'un fichier reste lisible (au plus une cinquantaine d'exigences), alignés sur la structure du CCTP ;
   - les **modules d'analyse** utiles (voir `format.md`, « analyse.md ») : `ecarts-offre` si notre offre est fournie ; `mutualisation`, `impacts-socle`, `droits-croises` seulement s'il y a un socle partagé par plusieurs périmètres ; tout autre module que ce projet justifie ;
   - l'**ordre des pièces** ;
   - les **exclusions** : les valeurs par défaut, ajustées si une pièce mêle sujets exclus et utiles ;
   - les premiers termes du glossaire.
3. Cherche les **points bloquants** : découpage non explicite, ambigu ou contradictoire entre pièces ; pièce essentielle citée mais absente ; périmètre du marché contradictoire ; pièce illisible. Chacun devient une question `bloquante` (format complet, avec citations), écrite dans `bdc/questions.md`.
4. Écris `bdc/config.yml`.
5. **Arrête-toi et présente au user** :
   - la forme du projet, les périmètres, les domaines, les modules retenus, en une page ;
   - les questions bloquantes et, pour chacune, les options possibles avec leur conséquence sur la structure ;
   - le volume prévu (pages, nombre de lots d'extraction).

   S'il y a une question bloquante, n'avance pas sans décision du user : réponse du client, choix d'une hypothèse (consignée dans la question et dans `journal.md`), ou arrêt. Sans question bloquante, demande quand même la validation de la structure avant de lancer l'extraction.

Terminé quand le user a validé la structure et que chaque question bloquante a une décision.

## 2. Extraction exhaustive

1. Découpe chaque pièce en **lots** de 10 à 20 pages, coupés sur des titres de section ; plus petits pour les pages denses (tableaux d'exigences, matrices). Un tableur : un lot par onglet, ou par bloc de 200 lignes. Une section qui est entièrement dans `exclusions` n'est pas extraite : inscris-la directement dans `hors-perimetre.md` et `couverture.md`.
2. Notre offre (MT…) s'extrait comme les autres pièces : ses engagements seront rapprochés des exigences à l'étape 4.
3. Lance un sous-agent par lot, avec cette consigne :

> Tu extrais de façon **exhaustive** le contenu utile aux développeurs des pages <a> à <b> de `<chemin>/bdc/sources/<CODE>.md` (pièce <CODE> : <intitulé>), pour une base de connaissance dont les formats sont dans `<skill>/references/format.md` et les paramètres (périmètres, domaines, exclusions) dans `<chemin>/bdc/config.yml`. Lis ces deux fichiers d'abord. Les repères `[[p.N]]` donnent les pages. <Si le registre signale une mise en page mélangée : « Le texte de ces pages est mal extrait : lis aussi le PDF `<original>` pages <a>-<b> avec l'outil Read. »>
>
> Écris ton résultat dans `<TRAVAIL>/<CODE>-<a>-<b>.md`, avec ces sections :
> - **Exigences** : au format des fiches d'exigence, avec des IDs provisoires `X-<CODE>-<a>-<k>` ; le champ `Domaine` en plus (code de config.yml) ; `Notre réponse` laissé vide. Une exigence par obligation distincte : une phrase qui impose trois choses donne trois exigences. Garde seuils, unités, délais et modalité (doit/peut) à l'identique.
> - **Entités**, **Acteurs**, **Interfaces**, **Processus** : au format de `format.md`, seulement les informations présentes dans ces pages.
> - **Termes** : chaque terme métier, sigle ou nom propre de système, avec sa définition si les pages la donnent.
> - **Anomalies** : tout ce qui est flou (critère non mesurable : « rapide », « ergonomique », « si besoin »), manquant (renvoi vers une pièce ou section absente, donnée sans format, cas non traité), erroné (calcul faux, renvoi cassé, numérotation incohérente) ou contradictoire à l'intérieur de ces pages, au format des fiches de question, sans ID.
> - **Hors périmètre** : sections écartées, selon `exclusions`, avec la raison.
> - **Couverture** : chaque section des pages <a>-<b> (titre, pages) → IDs provisoires produits, `hors périmètre`, `contexte` ou `doublon`. Aucune section sans statut.
>
> Règles : chaque élément porte une ou plusieurs lignes `Citation (<CODE> … p.N) : « … »` copiées mot pour mot depuis le fichier source ; ce qui n'est pas écrit est marqué `Certitude : déduit` avec le raisonnement. Lis chaque phrase et chaque cellule de tableau : les obligations se cachent dans les tableaux, les notes de bas de page, les légendes et les listes. Mots qui signalent une obligation : doit, devra, est tenu, obligatoire, impérativement, au minimum, au maximum, au plus tard, délai, garantit, le titulaire, le système, la solution. Ne résume pas : extrais.
>
> Ton message final : le chemin du fichier, puis le nombre d'éléments par section, en une ligne.

Terminé quand chaque lot a son fichier de travail.

## 3. Vérification adversariale

Pour chaque lot, un **autre** sous-agent que celui qui l'a extrait :

> Tu vérifies une extraction faite par quelqu'un d'autre ; pars du principe qu'elle contient des erreurs et des oublis. Source : pages <a> à <b> de `<chemin>/bdc/sources/<CODE>.md`. Extraction : `<TRAVAIL>/<CODE>-<a>-<b>.md`. Formats : `<skill>/references/format.md`.
>
> 1. Pour chaque élément : la citation existe-t-elle mot pour mot dans la source (vérifie avec `grep -F`), à la page indiquée ? La reformulation est-elle fidèle (rien d'ajouté, rien d'atténué, mêmes seuils, unités, modalité) ? `Nature`, `Type`, `Domaine`, `Périmètre` sont-ils justes ? Ce qui est marqué `explicite` l'est-il vraiment ?
> 2. Relis toute la source, phrase par phrase et cellule par cellule, et liste **tout ce qui manque** : obligation, règle, donnée, acteur, interface, terme, anomalie, section absente de la couverture.
>
> Corrige directement le fichier d'extraction (corrections et ajouts, au même format), puis ajoute à la fin une section **Vérification** : nombre d'éléments corrigés, ajoutés, retirés, avec une ligne par correction. Ton message final : le chemin du fichier et ces trois nombres.

Si un lot revient avec plus de 5 ajouts ou corrections importantes, relance une deuxième vérification sur ce lot. Recommence jusqu'à ce qu'une vérification ne trouve plus rien d'important.

Terminé quand chaque lot a passé une vérification sans ajout important.

## 4. Consolidation

Ordre imposé : les noms canoniques passent avant les exigences qui y renvoient.

1. **Glossaire et modèle** : un sous-agent reçoit tous les fichiers de travail. Il fusionne termes, entités, acteurs, interfaces et processus (un objet décrit dans plusieurs pièces = une fiche avec toutes ses citations), fixe les noms canoniques (`EN-…`, `AC-…`, `IF-…`, `PR-…`), signale chaque terme qui a plusieurs sens ou plusieurs noms (anomalie), et écrit `bdc/glossaire.md` et `bdc/modele/*.md`, dont la matrice des droits complète.
2. **Exigences, par périmètre et domaine** : un sous-agent par domaine (ou par couple périmètre × domaine), en parallèle. Chacun :
   - rassemble les exigences de son domaine dans tous les fichiers de travail (`grep -n "Domaine : <CODE>"`) ;
   - fusionne les doublons (même obligation dans plusieurs pièces = une exigence, plusieurs citations ; si les pièces divergent, c'est une anomalie `contradiction`) ;
   - attribue les IDs définitifs `EX-<DOMAINE>-001…` dans l'ordre du CCTP ;
   - remplace dans `Liens` les noms provisoires par les noms canoniques du modèle ;
   - si notre offre est fournie : remplit `Notre réponse` en cherchant dans `bdc/sources/MT.md` (et les autres pièces de l'offre) ce qui couvre chaque exigence, avec citation ; et crée une exigence `engagement supplémentaire` pour chaque engagement de l'offre lié à son domaine qui ne correspond à aucune demande ;
   - écrit le fichier d'exigences et rend une **table de correspondance** `ID provisoire → ID définitif` dans `<TRAVAIL>/correspondance-<DOMAINE>.md`.
3. Toi : construis `couverture.md` et `hors-perimetre.md` à partir des sections Couverture et Hors périmètre des lots, en remplaçant les IDs provisoires grâce aux tables de correspondance.

Terminé quand chaque fichier de la Bdc prévu au cadrage existe et que `verifier_bdc.py` ne signale plus d'ID provisoire `X-…`.

## 5. Analyse critique : challenger le dossier

Cette étape fait la valeur de la Bdc : chaque problème que le client peut lever maintenant coûte moins cher qu'en cours de développement. Lance en parallèle un sous-agent par angle ; chacun lit les fichiers de la Bdc (pas les pièces brutes, sauf pour vérifier une citation), écrit ses questions au format de `format.md` (sans ID) dans `<TRAVAIL>/critique-<angle>.md`, et classe chacune par gravité.

- **contradictions** : entre pièces, entre sections, entre texte et tableau, entre chiffres ; dire quelle pièce prévaut selon `ordre_des_pieces` et si l'écart a quand même un impact ;
- **flous** : exigences sans critère vérifiable, termes vagues, volumétries, performances ou délais absents, « à définir », « le cas échéant » ;
- **complétude du modèle** : entité sans cycle de vie, sans attributs ou sans volumétrie ; statut sans transition ; rôle sans droits ou droit sans rôle (cases `?` de la matrice) ; action prévue sans acteur ; interface sans format, fréquence ou authentification ; donnée personnelle sans durée de conservation ; processus sans cas d'erreur ; exigence sans critère d'acceptation testable ;
- **erreurs** : renvois cassés, pièces citées absentes, calculs faux, numérotation incohérente, sigles non définis ;
- **un angle par module activé** dans `config.yml` : produit en plus la section correspondante de `analyse.md`, dans `<TRAVAIL>/analyse-<module>.md`.

Ajoute les anomalies des fichiers d'extraction. Puis, toi :

1. Fusionne les doublons, attribue les `Q-NNN` (bloquantes d'abord), écris `bdc/questions.md` (en conservant les questions bloquantes du cadrage et leurs décisions).
2. Ajoute dans `Liens` des éléments concernés les `Q-…` qui les touchent.
3. Écris `bdc/analyse.md`.

Une question est bonne quand le client peut y répondre sans avoir le dossier sous les yeux : elle cite les passages, donne le contexte et propose si possible des options.

Terminé quand chaque angle a rendu son fichier et que chaque anomalie est devenue une question ou a été écartée avec sa raison dans `journal.md`.

## 6. Contrôles finaux

Chaque contrôle qui échoue renvoie à l'étape concernée ; ne passe au suivant qu'une fois le précédent vert.

1. **Citations** : `python3 <skill>/scripts/verifier_citations.py bdc` doit finir sur `0 échec(s)`. Pour chaque échec : corrige la citation (texte exact, bonne page), ou, si l'extraction est en cause (colonnes mélangées), vérifie à la main dans le PDF et note-le dans le registre.
2. **Couverture** : chaque section de chaque pièce a une ligne dans `couverture.md`, avec un statut et un renvoi. Compare avec le sommaire de chaque pièce : une section du sommaire absente de la couverture est un trou.
3. **Structure** : `python3 <skill>/scripts/verifier_bdc.py bdc --maj` doit finir sur `0 erreur(s)`. Il écrit aussi les récapitulatifs et les chiffres d'INDEX.
4. **Relecture d'ensemble** par un sous-agent neuf : « Tu es un développeur qui arrive sur le projet et n'a que `<chemin>/bdc/`. Lis INDEX.md puis parcours la Bdc. Liste ce qui est incompréhensible, ce qui manque pour commencer à concevoir et développer, et les incohérences entre fichiers. » Traite chaque point (correction, ajout ou question).

## 7. Finalisation

1. Écris `bdc/INDEX.md` (format dans `format.md`) et, s'il y a plusieurs périmètres, `bdc/perimetres.md`.
2. Ajoute l'entrée de génération dans `bdc/journal.md` : pièces, versions, décisions prises au cadrage, chiffres.
3. Propose au user d'ajouter au `CLAUDE.md` du dépôt (crée-le si besoin) ce bloc, pour que tout Claude de l'équipe consulte la Bdc :

   ```markdown
   ## Base de connaissance (Bdc)
   Le besoin du projet (appel d'offres et notre réponse) est décrit dans `bdc/`. Pour toute question sur le besoin, les exigences, le modèle ou les questions au client : lire `bdc/INDEX.md`, puis seulement les fichiers utiles ; citer les IDs et les sources. Pour la modifier ou en tirer un livrable : skill `bdc` (plugin `bdc@brieuc-claude-toolkit`).
   ```

4. Supprime le dossier de travail.
5. Rapport au user, court : forme du projet, chiffres (pièces, pages, exigences par périmètre, entités, questions par gravité), les 5 questions les plus importantes en une ligne chacune, les limites (pages transcrites d'images, extractions douteuses), puis la proposition todo (voir SKILL.md).
