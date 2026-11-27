#!/usr/bin/env python3
"""Extrait le texte d'une pièce en Markdown citable, pour bdc/sources/.

Usage : extraire.py <fichier> <CODE> <sortie.md>

PDF : repère [[p.N]] avant chaque page (pdftotext -layout, paquet poppler-utils).
XLSX : repère [[onglet:Nom]] avant chaque onglet, puis une ligne par rangée non vide : `12: A=… | C=…`.
DOC/DOCX/ODT/RTF et XLS/ODS : convertis d'abord par LibreOffice (soffice) en PDF ou XLSX.
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET

M = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


def sha256(chemin):
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def pdf(chemin):
    if not shutil.which("pdftotext"):
        sys.exit("pdftotext introuvable : installe poppler-utils.")
    texte = subprocess.run(["pdftotext", "-layout", chemin, "-"],
                           check=True, capture_output=True).stdout.decode("utf-8", "replace")
    pages = texte.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    # moins de 150 lettres : page blanche, scan, schéma, ou texte non extractible (seul un en-tête sort)
    vides = [str(i + 1) for i, p in enumerate(pages) if sum(ch.isalpha() for ch in p) < 150]
    corps = "".join(f"\n[[p.{i + 1}]]\n{p.rstrip()}\n" for i, p in enumerate(pages))
    return corps, f"{len(pages)} pages", vides


def valeur(cellule, partages):
    t = cellule.get("t")
    if t == "inlineStr":
        return "".join(x.text or "" for x in cellule.iter(f"{M}t"))
    v = cellule.find(f"{M}v")
    if v is None or v.text is None:
        return ""
    if t == "s":
        return partages[int(v.text)]
    if t == "b":
        return "VRAI" if v.text == "1" else "FAUX"
    return v.text


def xlsx(chemin):
    z = zipfile.ZipFile(chemin)
    partages = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall(f"{M}si"):
            # les <t> de lecture phonétique (rPh) ne font pas partie du texte
            morceaux = [t.text or "" for t in si.findall(f"{M}t")]
            morceaux += [t.text or "" for r in si.findall(f"{M}r") for t in r.findall(f"{M}t")]
            partages.append("".join(morceaux))
    rels = {r.get("Id"): r.get("Target")
            for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    corps, vides, onglets = [], [], 0
    for feuille in ET.fromstring(z.read("xl/workbook.xml")).find(f"{M}sheets"):
        cible = rels[feuille.get(R_ID)]
        cible = cible.lstrip("/") if cible.startswith("/") else "xl/" + cible
        racine = ET.fromstring(z.read(cible))
        nom = feuille.get("name")
        corps.append(f"\n[[onglet:{nom}]]\n")
        lignes = 0
        for rangee in racine.iter(f"{M}row"):
            cellules = []
            for c in rangee.findall(f"{M}c"):
                v = " ".join(valeur(c, partages).split())
                if v:
                    col = re.match(r"[A-Z]+", c.get("r", ""))
                    cellules.append(f"{col.group() if col else '?'}={v}")
            if cellules:
                corps.append(f"{rangee.get('r')}: " + " | ".join(cellules) + "\n")
                lignes += 1
        fusions = [m.get("ref") for m in racine.iter(f"{M}mergeCell")]
        if fusions:
            corps.append("Cellules fusionnées : " + ", ".join(fusions) + "\n")
        if not lignes:
            vides.append(nom)
        onglets += 1
    note = "\nLes dates Excel peuvent apparaître en nombre de jours depuis le 1899-12-30.\n"
    return "".join(corps) + note, f"{onglets} onglets", vides


def convertir(chemin, format_cible, dossier):
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        sys.exit(f"LibreOffice introuvable : exporte {chemin} en {format_cible.upper()} puis relance.")
    subprocess.run([soffice, "--headless", "--convert-to", format_cible, "--outdir", dossier, chemin],
                   check=True, capture_output=True)
    sortie = os.path.join(dossier, os.path.splitext(os.path.basename(chemin))[0] + "." + format_cible)
    if not os.path.exists(sortie):
        sys.exit(f"La conversion de {chemin} en {format_cible} a échoué.")
    return sortie


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    source, code, sortie = sys.argv[1:]
    ext = os.path.splitext(source)[1].lower()
    remarque = ""
    with tempfile.TemporaryDirectory() as tmp:
        chemin = source
        if ext in (".doc", ".docx", ".odt", ".rtf"):
            chemin, ext = convertir(source, "pdf", tmp), ".pdf"
            remarque = "converti en PDF par LibreOffice : la pagination peut différer de celle de Word"
        elif ext in (".xls", ".ods"):
            chemin, ext = convertir(source, "xlsx", tmp), ".xlsx"
            remarque = "converti en XLSX par LibreOffice"
        if ext == ".pdf":
            corps, taille, vides = pdf(chemin)
        elif ext in (".xlsx", ".xlsm"):
            corps, taille, vides = xlsx(chemin)
        else:
            sys.exit(f"Format non géré : {ext}")
    empreinte = sha256(source)
    entete = (f"# {code} : {os.path.basename(source)}\n\n"
              f"- sha256 : {empreinte}\n- taille : {taille}\n"
              + (f"- extraction : {remarque}\n" if remarque else "")
              + (f"- peu ou pas de texte : {', '.join(vides)}\n" if vides else ""))
    os.makedirs(os.path.dirname(os.path.abspath(sortie)), exist_ok=True)
    with open(sortie, "w", encoding="utf-8") as f:
        f.write(entete + corps)
    print(f"{code}\t{taille}\tsha256 {empreinte}\t{sortie}")
    if remarque:
        print(f"Remarque : {remarque}")
    if vides:
        print(f"Peu ou pas de texte (à regarder) : {', '.join(vides)}")


if __name__ == "__main__":
    main()
