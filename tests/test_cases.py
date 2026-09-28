"""Tests de la normalisation des cas et du filtre des cas de triage."""

from scripts.cases import is_triage_case, normalize_text


def test_case_and_whitespace_ignored():
    a = "Une femme de 52 ans  consulte\npour une prise de poids."
    b = "une femme de 52 ans consulte pour une prise de poids. "
    assert normalize_text(a) == normalize_text(b)


def test_non_breaking_space_ignored():
    assert normalize_text("52 ans") == normalize_text("52 ans")


def test_typographic_apostrophe_ignored():
    assert normalize_text("admis aux urgences d’un hôpital") == normalize_text("admis aux urgences d'un hôpital")


def test_different_texts_stay_different():
    assert normalize_text("Homme de 58 ans") != normalize_text("Homme de 85 ans")


# Exemples réels (raccourcis) de MediQAl et UltraMedical-Preference.
TRIAGE_CASES_FR = [
    "Monsieur G., 77 ans, est amené aux urgences par son fils. Il se plaint de douleurs thoraciques.",
    "Une femme de 60 ans consulte au service d'urgence pour une dyspnée.",
    "H., étudiante de 23 ans, présente une dysphagie douloureuse associée à une fièvre depuis 48 heures.",
    "Brigitte V., âgée de 25 ans, est enceinte de 8 mois. Elle est fébrile depuis 3 jours.",
]
NON_TRIAGE_CASES_FR = [
    "Au terme de 24 semaines de grossesse, la coupe 4 cavités du cœur fœtal montre un ventricule droit plus petit.",
    "Un couple vous demande des informations car la femme enceinte porte un fœtus atteint d'un tronc artériel commun.",
    "Lors d'un examen systématique à l'embauche, une bilharziose est diagnostiquée.",
    "Une jeune femme de 29 ans a eu une intervention de Mustard. Elle n'a aucun symptôme cardiaque.",
]
TRIAGE_CASES_EN = [
    "A 75-year-old man is brought to the emergency department because of worsening chest pain.",
    "A 6-month-old boy is brought to the emergency department because of fever and fast breathing.",
    "A 70 year old man presents with sudden weakness of the left arm.",
]
NON_TRIAGE_CASES_EN = [
    "Considering a 3-year-old child with sickle cell disease, what is the most suitable immunization approach?",
    "A 70 year old male patient dies with severe dementia. Autopsy demonstrates marked atrophy.",
    "Delve into the key enzymatic proteins that catalyze phosphorylation in neuronal signal transduction.",
    "A biology student is studying apoptosis pathways in a 45-year-old patient sample presented in class.",
]


def test_french_triage_cases_kept():
    assert all(is_triage_case(t, "fr") for t in TRIAGE_CASES_FR)


def test_french_cases_without_arrival_rejected():
    assert not any(is_triage_case(t, "fr") for t in NON_TRIAGE_CASES_FR)


def test_english_triage_cases_kept():
    assert all(is_triage_case(t, "en") for t in TRIAGE_CASES_EN)


def test_english_questions_rejected():
    assert not any(is_triage_case(t, "en") for t in NON_TRIAGE_CASES_EN)


def test_arrival_far_in_text_ignored():
    text = "Un enfant de 6 ans a un ventricule unique pallié en période néonatale. " * 5 + "Il est admis."
    assert not is_triage_case(text, "fr")
