"""Expressions régulières pour retirer les noms de patients des cas cliniques français,
et pour repérer un nom resté dans un texte (français ou anglais).

Presidio a été écarté car il remplaçait aussi des termes médicaux (« Protéine C
Réactive »), voir le notebook 02.
"""

import re

PATIENT = "[PATIENT]"
UPPER = "A-ZÉÈÀÂÎÔÛÏÜÖÇ"
LOWER = "a-zàâéèêëîïôûùç"
# « Monsier » : faute de frappe trouvée dans MediQAl (« Monsier Eric B. »)
TITLE = r"(?:Monsieur|Monsier|Madame|Mademoiselle|Mme|Mlle|Melle|Mr)"
# Un prénom ou un nom : une majuscule puis des minuscules, éventuellement composé (Jean-Luc)
NAME = rf"(?!{TITLE}\b)[{UPPER}][{LOWER}]+(?:-[{UPPER}][{LOWER}]+)?"

# Une initiale : suivie de points (« B. », « C... ») ou seule (« Mme Y », « Mr R 28 ans »)
INITIAL = rf"[{UPPER}](?:\.+|(?![{UPPER}{LOWER}'’-]))"
# « âgée » s'écrit parfois sans accent dans MediQAl (« Brigitte V., agée de 25 ans »)
AGED = "[âa]gée?"
AGE = rf"(?:{AGED} de )?\d{{1,3}} ?ans\b"

# Le titre est capturé avec son point éventuel, pour le garder : « M. Robert D » devient
# « M. [PATIENT] ».
# « Monsieur DUPONT », « Mr LUC... », « Monsieur Jean-Jacques TUR. » : nom en majuscules
TITLE_UPPER_SURNAME = re.compile(rf"\b({TITLE}\.?)\s+(?:{NAME}\s+)?[{UPPER}]{{2,}}\b\.*")
# « Mme Aline R. », « Monsieur Paul D... », « M. Robert D, âgé de 85 ans »
TITLE_FIRST_NAME_INITIAL = re.compile(rf"\b((?:{TITLE}|M)\.?)\s+{NAME}\s+{INITIAL}")
# « Monsieur B. », « Monsieur C... », « Mme Y »
TITLE_INITIAL = re.compile(rf"\b((?:{TITLE}|M)\.?)\s+{INITIAL}")
# Le prénom resté après la balise : « Monsieur [PATIENT] Daniel, âgé de 38 ans »,
# « Monsieur [PATIENT] Jean est âgé de 41 ans »
NAME_AFTER_PATIENT = re.compile(rf"\[PATIENT\][.\s]*{NAME}(?=,|\s+\d|\s+(?:est\s+)?{AGED}\b)")
# « Monsieur Durand », « Mme Barbie », « Madame Haz. ». Sans « M. », trop ambigu devant un
# mot en majuscule (« un nouveau produit M. La justification... »).
TITLE_SURNAME = re.compile(rf"\b({TITLE}\.?)\s+(?!\[PATIENT\]){NAME}\.*")
# « Brigitte V. est traitée », « Noé L. 10 ans » : prénom et initiale sans titre. Sans
# point, seulement devant un âge (« Marc X, 23 ans ») : ailleurs, « Protéine C Réactive ».
# Un nom abrégé en majuscules, seulement devant « âgé » (« Kévin REN., âgé de 16 mois ») :
# ailleurs, « Dosage TSH. ».
FIRST_NAME_INITIAL = re.compile(
    rf"\b(?P<name>{NAME})\s+"
    rf"(?:[{UPPER}](?:\.+(?=[\s,;:)]|$)|(?=,?\s+{AGE}))|[{UPPER}]{{2,}}\.+(?=,?\s+{AGED}\b))"
)
# « Damien, âgé de 6 ans », « Mouna, 03ans »
FIRST_NAME_AGE = re.compile(rf"\b(?P<name>{NAME})(?=,? {AGE})")

# Mots en majuscule qui ne sont pas des prénoms de patients, devant un âge (« Patiente,
# 45 ans ») ou devant une lettre (« Streptocoque A. », « Dr M. »). Liste construite en
# relisant les candidats sur MediQAl (notebook 02).
NOT_FIRST_NAMES = {
    "Homme", "Femme", "Dame", "Patient", "Patiente", "Malade", "Enfant", "Garçon", "Fille",
    "Nourrisson", "Adolescent", "Adolescente", "Jeune", "Sujet", "Mère", "Père", "Il", "Elle",
    "Lui", "Depuis", "Puberté", "Primigeste", "Appendicectomie", "Cockroft", "Maghrébine", "Alger",
    "Streptocoque", "Amphotéricine", "Pénicylline", "Pénicilline", "Vitamine", "Hépatite",
    "Protéine", "Facteur", "Groupe", "Type", "Hb", "Na", "Ig", "Dr", "Docteur",
}


def _replace_name(match):
    """Remplace le match par [PATIENT], sauf si le mot capturé n'est pas un prénom."""
    return match.group(0) if match.group("name") in NOT_FIRST_NAMES else PATIENT


# Les règles dans l'ordre où elles sont appliquées : (nom, motif, remplacement)
PATIENT_NAME_RULES = [
    ("titre + NOM", TITLE_UPPER_SURNAME, rf"\1 {PATIENT}"),
    ("titre + prénom + initiale", TITLE_FIRST_NAME_INITIAL, rf"\1 {PATIENT}"),
    ("titre + initiale", TITLE_INITIAL, rf"\1 {PATIENT}"),
    ("prénom après la balise", NAME_AFTER_PATIENT, PATIENT),
    ("titre + nom", TITLE_SURNAME, rf"\1 {PATIENT}"),
    ("prénom + initiale", FIRST_NAME_INITIAL, _replace_name),
    ("prénom + âge", FIRST_NAME_AGE, _replace_name),
]


def replace_patient_names(text, log=None):
    """Remplace les noms de patients par [PATIENT]. Renvoie le texte et True si un nom a
    été remplacé.

    `log` (un defaultdict(Counter), optionnel) compte les formes remplacées par règle."""
    original = text
    for rule_name, pattern, replacement in PATIENT_NAME_RULES:
        if log is not None:
            for m in pattern.finditer(text):
                if "name" not in pattern.groupindex or m.group("name") not in NOT_FIRST_NAMES:
                    log[rule_name][m.group(0)] += 1
        text = pattern.sub(replacement, text)
    # « Madame D.25 ans » : le point avalé avec l'initiale laisse la balise collée à l'âge
    text = re.sub(r"\[PATIENT\](?=\d)", PATIENT + " ", text)
    return text, text != original


# Motifs qui repèrent un nom resté dans un texte. Chaque motif capture le nom dans le
# groupe « name ».
LEFTOVER_NAME_FR = rf"(?P<name>[{UPPER}][{LOWER}]{{2,}}(?:-[ÉÈA-Z][{LOWER}]+)?)"
LEFTOVER_NAME_EN = r"(?P<name>[A-Z][a-z]{2,})"
LEFTOVER_PATTERNS = {
    "fr": {
        "titre + initiale": re.compile(rf"\b(?:Monsieur|Madame|Mademoiselle|Mme|Mlle|Mr|M)\.?\s+(?P<name>[{UPPER}])(?:\.|(?![{UPPER}{LOWER}'’-]))"),
        "titre + nom": re.compile(r"\b(?:Monsieur|Madame|Mademoiselle|Mme|Mlle|Mr|Me)\.? " + LEFTOVER_NAME_FR),
        "titre + NOM": re.compile(rf"\b(?:Monsieur|Madame|Mademoiselle|Mme|Mlle|Mr|Me)\.? (?P<name>[{UPPER}]{{2,}})\b"),
        "prénom + âge": re.compile(LEFTOVER_NAME_FR + rf"(?: [A-Z]\.*)?,? {AGE}"),
        "prénom + initiale": re.compile(LEFTOVER_NAME_FR + r" [A-Z]\.(?=[\s,])"),
    },
    "en": {
        "titre + nom": re.compile(r"\b(?:Mr|Mrs|Ms|Miss)\.? " + LEFTOVER_NAME_EN),
        "prénom + âge": re.compile(LEFTOVER_NAME_EN + r",? (?:a |an |aged )?\d{1,3}[- ]?(?:years?|yrs?)[- ]?old\b"),
        "je m'appelle": re.compile(r"\b(?:[Mm]y name is|[Tt]his is) " + LEFTOVER_NAME_EN),
        # Fiche patient : « Name: John Doe », « Patient Name: Jane Doe »
        "fiche patient": re.compile(r"\bName: " + LEFTOVER_NAME_EN),
    },
}
# Mots courants qui précèdent un âge ou suivent un titre sans être des noms : ceux des
# règles, plus les titres et des mots anglais
NOT_NAMES = NOT_FIRST_NAMES | {
    "Épouse", "Mari", "Monsieur", "Madame", "Mademoiselle", "Mme", "Mlle",
    "Male", "Female", "Man", "Woman", "Boy", "Girl", "Child", "Infant", "Baby", "Mother", "Father",
    "Wife", "Husband", "Doctor", "Old", "Year", "Years",
    # Débuts de phrase anglais : « For a 54-year-old male... », « Considering a 16-year-old... »
    "For", "Considering", "Consider", "Given", "The", "This", "That", "Her", "His", "She", "When",
    "Being", "What", "Which", "After", "Before", "During", "Assuming", "Suppose", "Imagine",
}


def find_leftover_names(text, language):
    """Renvoie les noms restés dans le texte, sous forme de (type de motif, match)."""
    return [
        (kind, m)
        for kind, pattern in LEFTOVER_PATTERNS[language].items()
        for m in pattern.finditer(text)
        if m.group("name") not in NOT_NAMES
    ]
