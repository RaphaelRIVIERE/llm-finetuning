"""Tests de la normalisation des cas, de la clé de cas et du filtre des cas de triage."""

from collections import Counter

from scripts.cases import (
    case_key, dedupe_cases, drop_short_vignettes, find_leaks, is_triage_case, normalize_text, remove_choices,
    remove_double_question_mark, split_cases,
)


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


# Un cas MediQAl et sa suite : même patient, un paragraphe de plus.
CASE_START = "Madame [PATIENT], 60 ans, est hospitalisée en urgence pour hyperthermie et frissons. Un myélome a été diagnostiqué."


def test_follow_up_case_has_same_key():
    follow_up = CASE_START + " Trois jours plus tard, elle devient confuse."
    assert case_key(follow_up) == case_key(CASE_START)


def test_case_key_ignores_case_and_whitespace():
    assert case_key(CASE_START.upper().replace(" ", "  ")) == case_key(CASE_START)


def test_different_cases_have_different_keys():
    other = "Monsieur [PATIENT], 45 ans, consulte pour une douleur thoracique apparue ce matin au repos."
    assert case_key(other) != case_key(CASE_START)


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


def test_dedupe_keeps_shortest_case_per_key():
    follow_up = CASE_START + " Trois jours plus tard, elle devient confuse."
    other = "Monsieur [PATIENT], 45 ans, consulte pour une douleur thoracique apparue ce matin au repos."
    records = [{"cas": t, "cle_cas": case_key(t)} for t in [follow_up, CASE_START, other]]
    assert sorted(r["cas"] for r in dedupe_cases(records)) == sorted([CASE_START, other])


VIGNETTE = (
    "A 15-year-old boy is brought to the emergency room for dyspnea and yellow skin. "
    "What is the most likely diagnosis?"
)


def test_choices_removed():
    text = VIGNETTE + "\n\nA. Acute leukemia\nB. Sideropenic anemia\nC. Hemolytic anemia\nD. Aplastic anemia"
    assert remove_choices(text) == VIGNETTE


def test_text_without_choices_returns_none():
    assert remove_choices(VIGNETTE + " A) Acute leukemia B) Hemolytic anemia") is None


def test_double_question_mark_removed():
    question = "Who is at risk for Parasites - Cysticercosis? ?"
    assert remove_double_question_mark(question) == "Who is at risk for Parasites - Cysticercosis?"


def test_normal_question_unchanged():
    question = "What is (are) Glaucoma ?"
    assert remove_double_question_mark(question) == question


def test_short_vignettes_dropped():
    short = {"source": "ultramedical_preference", "cas": "A 3 year old child comes with complaint of limp diagnosis is"}
    long = {"source": "ultramedical_preference", "cas": VIGNETTE}
    assert drop_short_vignettes([short, long]) == [long]


def test_short_mediqal_cases_kept():
    short = {"source": "mediqal", "cas": "Un homme se présente après avoir reçu de l'eau de javel dans un oeil"}
    assert drop_short_vignettes([short]) == [short]


def example(text, split):
    return {"cle_cas": case_key(text), "split": split}


def test_no_leak_when_each_case_in_one_split():
    other = "Monsieur [PATIENT], 45 ans, consulte pour une douleur thoracique apparue ce matin au repos."
    records = [example(CASE_START, "train"), example(CASE_START, "train"), example(other, "test")]
    assert find_leaks(records) == {}


def test_follow_up_in_other_split_is_a_leak():
    follow_up = CASE_START + " Trois jours plus tard, elle devient confuse."
    leaks = find_leaks([example(CASE_START, "train"), example(follow_up, "test")])
    assert leaks == {case_key(CASE_START): {"train", "test"}}


def test_leak_seen_between_sft_and_dpo():
    # Une question MedQuAD recopiée mot pour mot dans UltraMedical
    question = "What are the symptoms of Glaucoma ?"
    sft = [example(question, "test")]
    dpo = [example(question, "train")]
    assert find_leaks(sft + dpo) == {case_key(question): {"train", "test"}}


def unit(n, source, urgency_level=None):
    return {"cle_cas": f"{source} cas {n}", "source": source, "urgency_level": urgency_level}


def test_split_keeps_ratios_in_each_stratum():
    records = [unit(n, "mediqal", level) for level in ["maximum", "moderate", "deferred"] for n in range(100)]
    records += [unit(n, "medquad") for n in range(200)]
    splits = split_cases(records)
    counts = Counter((r["source"], r["urgency_level"], splits[r["cle_cas"]]) for r in records)
    for level in ["maximum", "moderate", "deferred"]:
        assert [counts["mediqal", level, split] for split in ["train", "validation", "test"]] == [80, 10, 10]
    assert [counts["medquad", None, split] for split in ["train", "validation", "test"]] == [160, 20, 20]


def test_split_puts_all_examples_of_a_case_together():
    # un cas de triage et deux questions QA sur le même patient
    records = []
    for n in range(50):
        records += [unit(n, "mediqal"), unit(n, "mediqal", "maximum"), unit(n, "mediqal")]
    splits = split_cases(records)
    assert find_leaks([{**r, "split": splits[r["cle_cas"]]} for r in records]) == {}
    assert Counter(splits.values()) == {"train": 40, "validation": 5, "test": 5}


def test_split_is_the_same_on_each_run():
    records = [unit(n, "mediqal", "moderate") for n in range(60)] + [unit(n, "medquad") for n in range(60)]
    assert split_cases(records) == split_cases(records)
