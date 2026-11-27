#!/usr/bin/env python3
"""Vérifie que chaque citation de la Bdc existe mot pour mot dans sa pièce, à la page annoncée.

Usage : verifier_citations.py <dossier bdc>

Lit les lignes `Citation (<CODE> … p.N) : « … »` (ou `<CODE> › Onglet!B12`) de tous les .md
hors sources/ et livrables/, et cherche le texte dans sources/<CODE>.md, espaces et apostrophes
normalisés. `[…]` sépare des morceaux qui doivent apparaître dans l'ordre.
Code de sortie 1 s'il y a au moins un échec.
"""
import os
import re
import sys

CITATION = re.compile(r"Citation \((\S+)([^)]*)\) : « (.+?) »")
REPERE = re.compile(r"\[\[(p\.\d+|onglet:[^\]]+)\]\]")
SAUT = re.compile(r"\[(?:…|\.\.\.)\]")


def normaliser(texte):
    texte = texte.replace("’", "'").replace("‘", "'").replace(" ", " ").replace(" ", " ")
    texte = texte.replace("“", '"').replace("”", '"').replace("«", '"').replace("»", '"')
    return " ".join(texte.split())


def charger(chemin):
    """Texte normalisé de la pièce + liste (position, repère) pour retrouver page ou onglet."""
    with open(chemin, encoding="utf-8") as f:
        brut = f.read()
    morceaux, reperes, pos = [], [], 0
    dernier = 0
    for m in REPERE.finditer(brut):
        avant = normaliser(brut[dernier:m.start()])
        if avant:
            morceaux.append(avant)
            pos += len(avant) + 1
        reperes.append((pos, m.group(1)))
        dernier = m.end()
    reste = normaliser(brut[dernier:])
    if reste:
        morceaux.append(reste)
    return " ".join(morceaux), reperes


def repere_a(reperes, position):
    courant = None
    for debut, rep in reperes:
        if debut > position:
            break
        courant = rep
    return courant


def chercher(texte, fragments):
    """Positions de chaque occurrence du premier fragment suivie des autres dans l'ordre."""
    positions, debut = [], texte.find(fragments[0])
    while debut >= 0:
        curseur = debut + len(fragments[0])
        for frag in fragments[1:]:
            i = texte.find(frag, curseur)
            if i < 0:
                return positions
            curseur = i + len(frag)
        positions.append(debut)
        debut = texte.find(fragments[0], debut + 1)
    return positions


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    bdc = sys.argv[1]
    sources, cache = os.path.join(bdc, "sources"), {}
    ok, echecs = 0, []
    for racine, dossiers, fichiers in os.walk(bdc):
        dossiers[:] = [d for d in dossiers if os.path.join(racine, d) not in
                       (sources, os.path.join(bdc, "livrables"))]
        for nom in sorted(fichiers):
            if not nom.endswith(".md"):
                continue
            chemin = os.path.join(racine, nom)
            with open(chemin, encoding="utf-8") as f:
                for num, ligne in enumerate(f, 1):
                    for m in CITATION.finditer(ligne):
                        code, ref, citation = m.groups()
                        ou = f"{os.path.relpath(chemin, bdc)}:{num}"
                        piece = os.path.join(sources, f"{code}.md")
                        if code not in cache:
                            cache[code] = charger(piece) if os.path.exists(piece) else None
                        if cache[code] is None:
                            echecs.append(f"{ou}  pièce inconnue : {code} (pas de sources/{code}.md)")
                            continue
                        texte, reperes = cache[code]
                        fragments = [normaliser(x) for x in SAUT.split(citation) if normaliser(x)]
                        if not fragments:
                            echecs.append(f"{ou}  citation vide")
                            continue
                        positions = chercher(texte, fragments)
                        if not positions:
                            # mot coupé en fin de ligne par pdftotext (« authenti- fication ») :
                            # on recolle, la page n'est alors pas vérifiée
                            if not chercher(texte.replace("- ", ""), [x.replace("- ", "") for x in fragments]):
                                echecs.append(f"{ou}  introuvable dans {code} : « {citation[:80]} »")
                            else:
                                ok += 1
                            continue
                        attendue = re.search(r"p\.(\d+)", ref)
                        trouvees = [repere_a(reperes, p) for p in positions]
                        if attendue and None not in trouvees and f"p.{attendue.group(1)}" not in trouvees:
                            echecs.append(f"{ou}  {code} : page annoncée p.{attendue.group(1)}, "
                                          f"texte trouvé en {', '.join(dict.fromkeys(trouvees))}")
                            continue
                        ok += 1
    for e in echecs:
        print(e)
    print(f"{ok} citation(s) vérifiée(s), {len(echecs)} échec(s)")
    sys.exit(1 if echecs else 0)


if __name__ == "__main__":
    main()
