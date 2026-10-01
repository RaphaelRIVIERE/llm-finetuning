"""Tests de la construction des exemples SFT, avec de fausses annotations."""

import json
from collections import Counter

from app.triage import StatutParsing, parser_sortie
from scripts.examples import (
    apply_translations, build_dpo_examples, build_qa_examples, build_triage_examples, keep_scored_preferences, sample_qa_examples,
)

CAS = "Homme de 62 ans, amené aux urgences pour une douleur thoracique depuis une heure."

SORTIE = {
    "urgency_level": "maximum",
    "specialty": "cardiology",
    "key_symptoms": ["douleur thoracique"],
    "red_flags": ["douleur thoracique au repos"],
    "justification": "Douleur thoracique récente chez un homme de 62 ans.",
    "recommendation": "Faire un ECG tout de suite.",
}


def annotation(valide=True):
    return {
        "id": "mediqal_cas_1",
        "langue": "fr",
        "source": "mediqal",
        "licence_source": "CC-BY-4.0",
        "niveau_confiance": "haut",
        "transformations": ["anonymisation_noms"],
        "cas": CAS,
        "cle_cas": "homme de 62 ans",
        "annotateur": "mistral-large-2512",
        "version_prompt": "aea0aafc7b85",
        "valide": valide,
        "sortie": SORTIE if valide else None,
        "antecedents": ["hypertension"] if valide else [],
        "constantes_vitales": {"fc": "110", "pa": None, "fr": None, "spo2": None, "temperature": None} if valide else {},
    }


SPLITS = {"homme de 62 ans": "test"}


def test_triage_example_has_case_and_json_answer():
    [example] = build_triage_examples([annotation()], SPLITS)
    assert example["instruction"] == CAS
    assert json.loads(example["reponse"]) == SORTIE
    assert parser_sortie(example["reponse"]).statut == StatutParsing.VALIDE


def test_triage_answer_starts_with_urgency_level():
    # le score de la courbe PR se lit juste après ce préfixe
    [example] = build_triage_examples([annotation()], SPLITS)
    assert example["reponse"].startswith('{"urgency_level": "maximum"')


def test_triage_example_takes_split_of_its_case():
    [example] = build_triage_examples([annotation()], SPLITS)
    assert example["split"] == "test"
    assert example["tache"] == "triage"
    assert example["urgency_level"] == "maximum"


def test_triage_example_keeps_clinical_metadata():
    [example] = build_triage_examples([annotation()], SPLITS)
    assert example["symptomes"] == ["douleur thoracique"]
    assert example["antecedents"] == ["hypertension"]
    assert example["constantes_vitales"]["fc"] == "110"
    assert example["transformations"] == ["anonymisation_noms", "annotation_triage"]


TRADUCTION = {
    "key_symptoms": ["chest pain"],
    "red_flags": ["chest pain at rest"],
    "justification": "Recent chest pain in a 62 year old man.",
    "recommendation": "Do an ECG right away.",
}


def test_translation_replaces_text_fields_only():
    [traduite] = apply_translations([annotation()], [{"id": "mediqal_cas_1", "valide": True, "traduction": TRADUCTION}])
    assert traduite["sortie"] == {**TRADUCTION, "urgency_level": "maximum", "specialty": "cardiology"}
    assert traduite["transformations"] == ["anonymisation_noms", "traduction_anglais"]
    # l'annotation d'origine n'est pas modifiée
    assert annotation()["sortie"] == SORTIE


def test_invalid_translation_ignored():
    [gardee] = apply_translations([annotation()], [{"id": "mediqal_cas_1", "valide": False, "traduction": None}])
    assert gardee == annotation()


def test_invalid_annotation_dropped():
    assert build_triage_examples([annotation(valide=False)], SPLITS) == []


def question(split=None):
    return {
        "id": "medquad_1",
        "langue": "en",
        "source": "medquad",
        "licence_source": "CC-BY-4.0",
        "split": split,
        "niveau_confiance": "moyen",
        "transformations": [],
        "instruction": "What is (are) Glaucoma ?",
        "reponse": "Glaucoma is a group of diseases that can damage the optic nerve.",
        "cle_cas": "what is (are) glaucoma ?",
        "symptomes": [],
        "antecedents": [],
        "constantes_vitales": {},
    }


SPLITS_QA = {"what is (are) glaucoma ?": "validation"}


def test_qa_example_takes_split_of_its_case():
    [example] = build_qa_examples([question()], SPLITS_QA)
    assert example["split"] == "validation"
    assert example["tache"] == "qa"
    assert example["instruction"] == "What is (are) Glaucoma ?"
    assert example["transformations"] == []


def test_qa_example_notes_a_changed_source_split():
    [example] = build_qa_examples([question(split="train")], SPLITS_QA)
    assert example["split"] == "validation"
    assert example["transformations"] == ["split_reassigne"]


def test_qa_sample_is_half_french_half_english():
    # beaucoup plus d'anglais que de français au départ, comme dans les sources
    examples = [
        {"id": f"{langue}_{split}_{n}", "langue": langue, "split": split}
        for langue, taille in [("fr", 1000), ("en", 5000)]
        for split, part in [("train", 0.8), ("validation", 0.1), ("test", 0.1)]
        for n in range(int(taille * part))
    ]
    echantillon = sample_qa_examples(examples, 200)
    comptes = Counter((e["langue"], e["split"]) for e in echantillon)
    for langue in ["fr", "en"]:
        assert [comptes[langue, split] for split in ["train", "validation", "test"]] == [80, 10, 10]
    assert len({e["id"] for e in echantillon}) == 200
    assert sample_qa_examples(examples, 200) == echantillon


def test_dpo_pair_takes_split_of_its_case():
    paire = {
        "id": "ultramedical_preference_1",
        "source": "ultramedical_preference",
        "split": "train",
        "transformations": [],
        "prompt": "What is (are) Glaucoma ?",
        "chosen": "Glaucoma is a group of diseases that can damage the optic nerve.",
        "rejected": "Glaucoma is a skin disease.",
        "cle_cas": "what is (are) glaucoma ?",
    }
    [example] = build_dpo_examples([paire], SPLITS_QA)
    # la question MedQuAD de même clé est en validation, sa paire DPO aussi
    assert example["split"] == "validation"
    assert example["transformations"] == ["split_reassigne"]
    assert example["tache"] == "qa"
    assert paire["split"] == "train"


def test_pairs_without_better_score_dropped():
    paires = [
        {"id": "meilleur", "score_chosen": 5.0, "score_rejected": 4.0},
        {"id": "egal", "score_chosen": 3.0, "score_rejected": 3.0},
        {"id": "moins bon", "score_chosen": 3.0, "score_rejected": 4.0},
    ]
    assert [p["id"] for p in keep_scored_preferences(paires)] == ["meilleur"]


def test_triage_and_qa_examples_have_same_fields():
    [triage] = build_triage_examples([annotation()], SPLITS)
    [qa] = build_qa_examples([question()], SPLITS_QA)
    assert set(triage) == set(qa)
