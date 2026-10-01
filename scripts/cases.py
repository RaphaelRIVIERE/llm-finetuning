"""Unité de cas de chaque source, pour le dédoublonnage, le découpage et le contrôle
de fuite. Pas de dépendance lourde, pour que les tests tournent dans la CI.

Ce qu'est un cas selon la source :
- MediQAl : le texte du cas clinique (plusieurs questions portent sur le même cas).
  Sans cas clinique, la question seule.
- MedQuAD et FrenchMedMCQA : la question.
- UltraMedical-Preference : le prompt.
"""

import re
import unicodedata
from collections import defaultdict

from sklearn.model_selection import train_test_split

WHITESPACE = re.compile(r"\s+")
# Les sources mélangent apostrophe droite et typographique (« d'urgence », « d’urgence »)
APOSTROPHES = str.maketrans({"’": "'", "‘": "'", "ʼ": "'"})


def normalize_text(text):
    """Normalise le texte pour comparer deux cas (unicode, apostrophes, casse, espaces)."""
    text = unicodedata.normalize("NFKC", text).translate(APOSTROPHES)
    text = WHITESPACE.sub(" ", text)
    return text.strip().casefold()


# Certains cas MediQAl sont la suite d'un autre : même patient, un paragraphe de plus.
# 100 caractères regroupe le plus de suites sans réunir des cas différents (notebook 01).
CASE_KEY_LENGTH = 100


def case_key(text):
    """Début du texte normalisé. À calculer sur le texte anonymisé."""
    return normalize_text(text)[:CASE_KEY_LENGTH]


# Filtre des cas de triage : garde les cas où un patient arrive avec un problème, les seuls
# qu'on peut annoter en niveau d'urgence. Règles écrites en lisant des cas réels (notebook
# 01). L'arrivée du patient est décrite dans les premières phrases, on ne regarde que le
# début du texte pour éviter les faux positifs plus loin (« à l'examen », « admis » dans
# les antécédents...).
HEAD_LENGTH = 300

# Français (MediQAl) : un verbe d'arrivée, ou une plainte récente datée.
ARRIVAL_FR = re.compile(
    r"consult|urgences?\b|\badmise?\b|hospitalisée?|amenée?|conduite?|adressée?|orientée?"
    r"|se présente|est présentée?|vous est confiée?|accueill|recevez|examinée?\b|examin(?:ez|er)\b"
    r"|vous voyez|appel|samu|smur|pompiers|\bvient (?:vous|pour|en)|trouvée? inanimée?|retrouvée?"
)
COMPLAINT_FR = re.compile(
    r"\b(?:présente|souffre|a présenté|se plaint|se dit|est fébrile)\b[^.]{0,120}"
    r"\b(?:depuis (?:\d+|quelques?|une|deux|trois|hier)|brutal|en quelques|ce matin|la veille|heures?\b|installation)"
)
# Situations sans patient qui arrive : diagnostic prénatal, conseil demandé par un
# confrère ou un couple, médecine du travail, suivi d'un patient sans symptôme.
EXCLUDED_FR = re.compile(
    r"fœt|foet|vous demande (?:conseil|votre avis|des informations)|vous interroge"
    r"|médecine du travail|visite (?:médicale|d.embauche)|examen systématique|bilan systématique"
    r"|aucun symptôme|génotyp"
)

# Anglais (UltraMedical-Preference) : un âge et un verbe d'arrivée au début. Beaucoup de
# prompts sont des questions de cours, l'âge seul ne suffit pas.
AGE_EN = re.compile(
    r"\b\d{1,3}[- ]?(?:years?|yrs?|months?|weeks?|days?)[- ]old\b|\bnewborn\b|\bneonate\b|\binfant\b"
)
ARRIVAL_EN = re.compile(
    r"\bpresents?\b|\bpresented\b|\bpresenting\b|\b(?:is|was) brought\b|\b(?:comes|came) (?:to|in)\b"
    r"|\b(?:is|was) admitted\b|\bvisits\b|\barrives\b|\b(?:is|was) (?:evaluated|seen|referred)\b"
    r"|\bcomplain|\bemergency (?:department|room)\b|\bconsults\b"
)
# Questions de sciences fondamentales habillées en cas : autopsie, étudiant, expérience.
EXCLUDED_EN = re.compile(
    r"\bautopsy\b|\bdied\b|\bdies\b|\bstudent\b|\bresearcher|\bmice\b|\bmouse\b|\brats?\b"
    r"|\bexperiment|\bvolunteers?\b"
)


def is_triage_case(text, language):
    """Dit si le texte décrit un patient qui arrive avec un problème. Laisse passer du
    bruit, la relecture fait le tri final."""
    head = normalize_text(text)[:HEAD_LENGTH]
    if language == "fr":
        arrival = ARRIVAL_FR.search(head) or COMPLAINT_FR.search(head)
        return bool(arrival) and not EXCLUDED_FR.search(head)
    if language == "en":
        arrival = AGE_EN.search(head) and ARRIVAL_EN.search(head)
        return bool(arrival) and not EXCLUDED_EN.search(head)
    raise ValueError(f"langue non gérée : {language}")


def dedupe_cases(records):
    """Garde un seul cas par `cle_cas`, le plus court : c'est l'arrivée du patient, les
    textes plus longs de la même clé ajoutent la suite de sa prise en charge."""
    par_cle = {}
    for record in records:
        garde = par_cle.get(record["cle_cas"])
        if garde is None or len(record["cas"]) < len(garde["cas"]):
            par_cle[record["cle_cas"]] = record
    return list(par_cle.values())


# Choix d'un QCM UltraMedical : une ligne qui commence par « A. », puis B, C...
CHOICES_START = re.compile(r"\n\s*A\.\s")


def remove_choices(text):
    """Retire les choix du QCM à la fin d'une vignette, qui soufflent le diagnostic.
    Renvoie None si le texte n'a pas de choix dans ce format."""
    starts = list(CHOICES_START.finditer(text))
    if not starts:
        return None
    # le dernier « A. » : un « A. » plus haut ferait partie du cas
    return text[:starts[-1].start()].strip()


# Certaines questions MedQuAD finissent par un point d'interrogation en trop (« ...? ? »)
DOUBLE_QUESTION_MARK = re.compile(r"\?\s*\?$")


def remove_double_question_mark(text):
    """Retire le point d'interrogation en trop à la fin d'une question."""
    return DOUBLE_QUESTION_MARK.sub("?", text.strip())


def drop_short_vignettes(records):
    """Écarte les vignettes UltraMedical plus courtes que la clé de cas. La clé d'une
    vignette aussi courte ne correspond plus à celle de son prompt d'origine, choix
    compris, et la paire DPO pourrait partir dans un autre split. Elles sont aussi trop
    pauvres pour être triées (« A neonate presented to OPD with following features »).
    Les cas MediQAl courts sont gardés : ils n'ont pas de choix, leur clé ne change pas."""
    return [
        record for record in records
        if record["source"] != "ultramedical_preference" or len(normalize_text(record["cas"])) >= CASE_KEY_LENGTH
    ]


def split_cases(records, seed=42):
    """Découpe par cas en train (80 %), validation (10 %) et test (10 %), toutes sources
    ensemble. Chaque record a une `cle_cas`, une `source` et, pour un cas de triage
    annoté, un `urgency_level`. Tous les records d'une même clé vont dans le même split.
    Le tirage est stratifié par source et par niveau d'urgence. Renvoie {cle_cas: split}."""
    strates = {}
    for record in records:
        # le cas de triage annoté donne sa strate à toute la clé
        if record["cle_cas"] not in strates or record.get("urgency_level"):
            strates[record["cle_cas"]] = (record["source"], record.get("urgency_level"))
    cles = sorted(strates)

    train, reste = train_test_split(
        cles, test_size=0.2, stratify=[str(strates[cle]) for cle in cles], random_state=seed
    )
    validation, test = train_test_split(
        reste, test_size=0.5, stratify=[str(strates[cle]) for cle in reste], random_state=seed
    )
    splits = {}
    for split, cles_du_split in [("train", train), ("validation", validation), ("test", test)]:
        for cle in cles_du_split:
            splits[cle] = split
    return splits


def find_leaks(records):
    """Contrôle de fuite : les clés de cas présentes dans plusieurs splits. Chaque record
    a une `cle_cas` et un `split`. On peut passer le SFT et le DPO ensemble, pour voir
    aussi les fuites d'un dataset à l'autre. Renvoie {cle: splits}, vide sans fuite."""
    splits_par_cle = defaultdict(set)
    for record in records:
        splits_par_cle[record["cle_cas"]].add(record["split"])
    return {cle: splits for cle, splits in splits_par_cle.items() if len(splits) > 1}
