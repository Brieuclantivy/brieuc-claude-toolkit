# Report template

File: `SECURITY_AUDIT_<YYYY-MM-DD>.md` at the project root. Language: French. Write for a developer who knows the project but has not read your notes: every finding must stand on its own.

Sort findings Critique -> Faible. Number them `VULN-01`, `VULN-02`... Omit sections that would be empty rather than writing "N/A", except "Ce qui n'a pas été testé", which is always present.

````markdown
# Audit de sécurité - <nom du projet>

> ⚠️ Document confidentiel : il décrit comment exploiter le projet. Ne pas committer ni partager publiquement.
> Aucune modification n'a été apportée au code du projet lors de cet audit.

- **Date** : <YYYY-MM-DD>
- **Périmètre** : <dossiers/services analysés, version ou commit si git>
- **Méthode** : analyse statique, <outils exécutés>, tests dynamiques locaux (<oui/non + environnement>)

## 1. Synthèse

<3-6 lignes : niveau de risque global, les 2-3 problèmes les plus urgents, ce qu'il faut corriger en premier.>

| Sévérité | Nombre |
|---|---|
| Critique | n |
| Élevée | n |
| Moyenne | n |
| Faible | n |
| Info | n |

| ID | Titre | Sévérité | Statut | Emplacement |
|---|---|---|---|---|
| VULN-01 | ... | Critique | Confirmé | `src/...:42` |

## 2. Surface d'attaque

<Stack, points d'entrée, mécanisme d'authentification, données sensibles, composants exposés. Court.>

## 3. Vulnérabilités

### VULN-01 - <titre court et précis>

- **Sévérité** : Critique | Élevée | Moyenne | Faible | Info  (CVSS ~x.x si estimable)
- **Statut** : Confirmé | Probable | À vérifier
- **Catégorie** : CWE-xxx / OWASP A0x:2021 - <nom>
- **Emplacement** : `chemin/fichier.ext:ligne` (+ autres occurrences)
- **Prérequis** : <non authentifié / compte utilisateur / admin / interaction utilisateur>

**Description**
<Ce qui ne va pas et pourquoi, en citant le code concerné (extrait court).>

**Impact**
<Ce qu'un attaquant peut concrètement faire : lire les données de qui, prendre le contrôle de quoi.>

**Reproduction**
Environnement : <dev local, http://localhost:3000, données de seed...>
1. <étape>
2. <commande `curl` ou payload exact>
3. **Résultat attendu (sain)** : ... / **Résultat observé (vulnérable)** : ...

**Preuve**
<Extrait de réponse/log, secrets masqués. Si non testé dynamiquement, dire pourquoi et détailler le raisonnement code.>

**Correction recommandée**
<Explication de la correction + extrait de code corrigé. Proposé seulement, non appliqué.>

```<lang>
// avant
...
// après
...
```

**Références** : <CWE, OWASP cheat sheet, CVE...>

---

(répéter pour chaque vulnérabilité)

## 4. Points positifs
<Bonnes pratiques constatées à conserver (ex. requêtes paramétrées partout, mots de passe en argon2...).>

## 5. Recommandations de durcissement
<Améliorations non liées à une faille précise : en-têtes, rotation des secrets, CI de scan, monitoring...>

## 6. Ce qui n'a pas été testé
<Zones non couvertes et pourquoi : services distants, code absent, environnement impossible à lancer, classes de failles non applicables, outils non installés. Un audit sans trouvaille dans une zone non testée ne prouve rien.>

## 7. Annexes
- Outils exécutés et versions
- Dépendances vulnérables (tableau : paquet, version, CVE, version corrigée)
- Secrets détectés (masqués) et leur emplacement, avec rappel de les **révoquer** (les retirer du code ne suffit pas s'ils sont dans l'historique git)
````

## Severity guide
- **Critique** : exploitable sans authentification (ou avec compte trivial) menant à RCE, prise de contrôle de compte/admin, fuite massive de données, secrets de production exposés.
- **Élevée** : exploitation réaliste avec un compte utilisateur ou une interaction simple : IDOR sur données sensibles, SQLi authentifiée, XSS stocké, SSRF interne.
- **Moyenne** : nécessite des conditions particulières ou impact limité : CSRF sur action modérée, XSS réfléchi, énumération d'utilisateurs, dépendance vulnérable non atteignable directement.
- **Faible** : durcissement manquant à impact faible : en-têtes, cookies sans flag dans un contexte limité, verbosité d'erreurs.
- **Info** : bonne pratique, dette de sécurité, pas d'exploitation directe.
