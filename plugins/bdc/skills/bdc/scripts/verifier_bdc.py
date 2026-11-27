#!/usr/bin/env python3
"""Contrôle la structure d'une Bdc et tient à jour ses récapitulatifs.

Usage : verifier_bdc.py <dossier bdc> [--maj]

Contrôles : marqueurs de conflit git, IDs définis deux fois, IDs cités mais jamais définis,
IDs provisoires restants, champs obligatoires et valeurs autorisées des exigences, questions et tickets,
périmètres et domaines connus de config.yml, lignes de couverture.md complètes,
récapitulatifs à jour.

--maj réécrit les récapitulatifs (entre <!-- recap --> et <!-- /recap --> dans questions.md
et chaque fichier d'exigences, entre <!-- chiffres --> et <!-- /chiffres --> dans INDEX.md).
Code de sortie 1 s'il reste au moins une erreur.
"""
import os
import re
import sys

ID_DEF = re.compile(r"^### (EX-[A-Z0-9]+-\d{3}|Q-\d{3}|T-\d{3}|(?:EN|AC|IF|PR)-[A-Z][A-Za-z0-9]*)(?: : (.*))?\s*$")
ID_REF = re.compile(r"(?<![\w-])(EX-[A-Z0-9]+-\d{3}|Q-\d{3}|T-\d{3}|(?:EN|AC|IF|PR)-[A-Z][A-Za-z0-9]*)(?![\w-])")
PROVISOIRE = re.compile(r"(?<![\w-])X-[A-Z0-9]+-\d+-\d+")
CHAMP = re.compile(r"^- ([^:]+?) : (.*)$")
CONFLIT = re.compile(r"^(<<<<<<< |=======\s*$|>>>>>>> )")

VALEURS = {
    "EX": {
        "Type": ["fonctionnelle", "règle de gestion", "technique", "sécurité", "performance", "exploitation",
                 "accessibilité", "données", "recette", "contractuelle"],
        "Nature": ["obligatoire", "souhaitée", "optionnelle", "variante", "PSE"],
        "Certitude": ["explicite", "déduit"],
        "Notre réponse": ["engagé", "partiel", "non traité", "engagement supplémentaire", "sans offre"],
    },
    "Q": {
        "Statut": ["ouverte", "posée", "répondue", "sans objet"],
        "Gravité": ["bloquante", "majeure", "mineure"],
        "Type": ["contradiction", "flou", "manque", "erreur", "incohérence offre", "risque"],
    },
    "T": {"Statut": ["à faire", "en cours", "fait", "obsolète"]},
}
OBLIGATOIRES = {
    "EX": ["Périmètre", "Type", "Nature", "Certitude", "Notre réponse"],
    "Q": ["Statut", "Gravité", "Type", "Périmètre", "Contexte", "Question pour le client"],
    "T": ["Statut", "Périmètre", "Exigences"],
}
STATUTS_COUVERTURE = ["extrait", "hors périmètre", "contexte", "doublon"]
ORDRE_STATUT = {"ouverte": 0, "posée": 1, "répondue": 2, "sans objet": 3}
ORDRE_GRAVITE = {"bloquante": 0, "majeure": 1, "mineure": 2}


def lire_config(chemin):
    perimetres, domaines, section = ["tous"], [], None
    if not os.path.exists(chemin):
        return None, None
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.split("#")[0].rstrip()
            if re.match(r"^\S", ligne):
                section = ligne.split(":")[0].strip()
            elif section == "perimetres" and (m := re.match(r"^\s*-\s*id:\s*(\S+)", ligne)):
                perimetres.append(m.group(1))
            elif section == "domaines" and (m := re.match(r"^\s+([A-Z0-9]+):", ligne)):
                domaines.append(m.group(1))
    return perimetres, domaines


def fichiers_md(bdc):
    exclus = {os.path.join(bdc, "sources"), os.path.join(bdc, "livrables")}
    for racine, dossiers, fichiers in os.walk(bdc):
        dossiers[:] = sorted(d for d in dossiers if os.path.join(racine, d) not in exclus)
        for nom in sorted(fichiers):
            if nom.endswith(".md"):
                yield os.path.join(racine, nom)


def fiches(lignes):
    """Découpe en fiches : (id, titre, n° de ligne, champs, texte, supprimée)."""
    resultat, courante = [], None
    for num, ligne in enumerate(lignes, 1):
        if ligne.startswith("#"):
            courante = None
            m = ID_DEF.match(ligne)
            if m:
                courante = {"id": m.group(1), "titre": (m.group(2) or "").strip(), "ligne": num,
                            "champs": {}, "texte": ligne}
                resultat.append(courante)
            continue
        if courante is not None:
            courante["texte"] += ligne
            m = CHAMP.match(ligne.rstrip("\n"))
            if m and m.group(1) not in courante["champs"]:
                courante["champs"][m.group(1)] = m.group(2).strip()
    for f in resultat:
        f["supprimee"] = "[supprimé" in f["texte"]
    return resultat


def recap_questions(qs):
    actives = [q for q in qs if not q["supprimee"]]
    def cle(q):
        statut = q["champs"].get("Statut", "")
        return (min((v for k, v in ORDRE_STATUT.items() if statut.startswith(k)), default=9),
                ORDRE_GRAVITE.get(q["champs"].get("Gravité", ""), 9), q["id"])
    lignes = ["| ID | statut | gravité | périmètre | titre |", "|---|---|---|---|---|"]
    for q in sorted(actives, key=cle):
        c = q["champs"]
        lignes.append(f"| {q['id']} | {c.get('Statut', '')} | {c.get('Gravité', '')} | "
                      f"{c.get('Périmètre', '')} | {q['titre']} |")
    return "\n".join(lignes)


def recap_exigences(exs):
    lignes = ["| ID | titre | type | nature | réponse | questions |", "|---|---|---|---|---|---|"]
    for e in exs:
        if e["supprimee"]:
            continue
        c = e["champs"]
        questions = ", ".join(sorted(set(re.findall(r"Q-\d{3}", c.get("Liens", "")))))
        lignes.append(f"| {e['id']} | {e['titre']} | {c.get('Type', '')} | {c.get('Nature', '')} | "
                      f"{c.get('Notre réponse', '')} | {questions} |")
    return "\n".join(lignes)


def remplacer_bloc(contenu, marqueur, nouveau):
    m = re.search(rf"<!-- {marqueur} -->(.*?)<!-- /{marqueur} -->", contenu, re.S)
    if not m:
        return None, False
    bloc = f"\n{nouveau}\n" if "\n" in nouveau else nouveau
    return contenu[:m.start(1)] + bloc + contenu[m.end(1):], m.group(1).strip() != nouveau.strip()


def main():
    args = [a for a in sys.argv[1:] if a != "--maj"]
    if len(args) != 1:
        sys.exit(__doc__)
    bdc, maj = args[0], "--maj" in sys.argv
    erreurs, majs = [], []
    perimetres, domaines = lire_config(os.path.join(bdc, "config.yml"))
    if perimetres is None:
        erreurs.append("config.yml absent")

    definitions, references, toutes_fiches = {}, [], {}
    for chemin in fichiers_md(bdc):
        rel = os.path.relpath(chemin, bdc)
        with open(chemin, encoding="utf-8") as f:
            lignes = f.readlines()
        for num, ligne in enumerate(lignes, 1):
            if CONFLIT.match(ligne):
                erreurs.append(f"{rel}:{num}  marqueur de conflit git")
            for m in PROVISOIRE.finditer(ligne):
                erreurs.append(f"{rel}:{num}  ID provisoire restant : {m.group()}")
            if not ID_DEF.match(ligne):
                references += [(m.group(1), rel, num) for m in ID_REF.finditer(ligne)]
        toutes_fiches[rel] = fiches(lignes)
        for fi in toutes_fiches[rel]:
            definitions.setdefault(fi["id"], []).append(f"{rel}:{fi['ligne']}")
            genre = next((g for g in VALEURS if fi["id"].startswith(g + "-")), None)
            if genre is None or fi["supprimee"]:
                continue
            ou = f"{rel}:{fi['ligne']}  {fi['id']}"
            for champ in OBLIGATOIRES[genre]:
                if not fi["champs"].get(champ):
                    erreurs.append(f"{ou} : champ « {champ} » manquant")
            for champ, permises in VALEURS[genre].items():
                valeur = fi["champs"].get(champ)
                if valeur and not any(valeur.startswith(p) for p in permises):
                    erreurs.append(f"{ou} : {champ} « {valeur} » hors des valeurs ({', '.join(permises)})")
            if genre == "EX" and "Citation (" not in fi["texte"] and "- Source :" not in fi["texte"]:
                erreurs.append(f"{ou} : ni Citation ni Source")
            if perimetres and fi["champs"].get("Périmètre"):
                for p in re.split(r",\s*", fi["champs"]["Périmètre"].split("(")[0]):
                    if p.strip() and p.strip() not in perimetres:
                        erreurs.append(f"{ou} : périmètre « {p.strip()} » absent de config.yml")
            if genre == "EX" and domaines is not None and fi["id"].split("-")[1] not in domaines:
                erreurs.append(f"{ou} : domaine « {fi['id'].split('-')[1]} » absent de config.yml")

    for ident, lieux in sorted(definitions.items()):
        if len(lieux) > 1:
            erreurs.append(f"{ident} défini plusieurs fois : {', '.join(lieux)}")
    for ident, rel, num in references:
        if ident not in definitions:
            erreurs.append(f"{rel}:{num}  {ident} cité mais défini nulle part")

    couverture = os.path.join(bdc, "couverture.md")
    if os.path.exists(couverture):
        with open(couverture, encoding="utf-8") as f:
            lignes = f.readlines()
        for num, ligne in enumerate(lignes, 1):
            suivante = lignes[num] if num < len(lignes) else ""
            if not ligne.startswith("|") or ligne.startswith("|-") or suivante.startswith("|-"):
                continue
            cellules = [c.strip() for c in ligne.strip().strip("|").split("|")]
            if len(cellules) < 4 or cellules[2] not in STATUTS_COUVERTURE or not cellules[3]:
                erreurs.append(f"couverture.md:{num}  ligne incomplète ou statut invalide "
                               f"({' / '.join(STATUTS_COUVERTURE)})")

    # récapitulatifs
    a_ecrire = {}
    for rel, fis in toutes_fiches.items():
        if rel == "questions.md":
            nouveau = recap_questions([f for f in fis if f["id"].startswith("Q-")])
        elif rel.startswith("exigences" + os.sep):
            nouveau = recap_exigences([f for f in fis if f["id"].startswith("EX-")])
        else:
            continue
        a_ecrire[rel] = ("recap", nouveau)
    exigences = sum(1 for fis in toutes_fiches.values() for f in fis
                    if f["id"].startswith("EX-") and not f["supprimee"])
    qs = [f for f in toutes_fiches.get("questions.md", []) if not f["supprimee"]]
    ouvertes = [q for q in qs if q["champs"].get("Statut", "").startswith(("ouverte", "posée"))]
    bloquantes = sum(1 for q in ouvertes if q["champs"].get("Gravité") == "bloquante")
    pieces = 0
    registre = os.path.join(bdc, "sources", "registre.md")
    if os.path.exists(registre):
        with open(registre, encoding="utf-8") as f:
            lignes = f.readlines()
        pieces = sum(1 for i, l in enumerate(lignes) if l.startswith("|") and not l.startswith("|-")
                     and not (i + 1 < len(lignes) and lignes[i + 1].startswith("|-")))
    a_ecrire["INDEX.md"] = ("chiffres", f"{pieces} pièces, {exigences} exigences, {len(ouvertes)} questions "
                                        f"ouvertes dont {bloquantes} bloquantes.")
    for rel, (marqueur, nouveau) in a_ecrire.items():
        chemin = os.path.join(bdc, rel)
        if not os.path.exists(chemin):
            erreurs.append(f"{rel} absent")
            continue
        with open(chemin, encoding="utf-8") as f:
            contenu = f.read()
        resultat, change = remplacer_bloc(contenu, marqueur, nouveau)
        if resultat is None:
            erreurs.append(f"{rel} : marqueurs <!-- {marqueur} --> / <!-- /{marqueur} --> absents")
        elif change and maj:
            with open(chemin, "w", encoding="utf-8") as f:
                f.write(resultat)
            majs.append(rel)
        elif change:
            erreurs.append(f"{rel} : récapitulatif périmé, relance avec --maj")

    for e in erreurs:
        print(e)
    for rel in majs:
        print(f"mis à jour : {rel}")
    print(f"{len(definitions)} ID(s), {len(erreurs)} erreur(s)")
    sys.exit(1 if erreurs else 0)


if __name__ == "__main__":
    main()
