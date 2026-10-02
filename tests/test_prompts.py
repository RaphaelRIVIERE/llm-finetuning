"""Tests de la construction des prompts."""

import pytest

from app.prompts import CONSIGNE_TRIAGE, construire_prompt
from app.triage import Specialty, UrgencyLevel

CAS = "Homme de 62 ans, amené aux urgences pour une douleur thoracique depuis une heure."


def test_triage_prompt_has_case_and_closed_lists():
    prompt = construire_prompt("triage", CAS)
    assert f"Cas : {CAS}" in prompt
    for valeur in list(UrgencyLevel) + list(Specialty):
        assert valeur.value in prompt


def test_qa_prompt_has_question_and_no_json_instruction():
    prompt = construire_prompt("qa", "What is (are) Glaucoma ?")
    assert "Question : What is (are) Glaucoma ?" in prompt
    assert "JSON" not in prompt


def test_prompt_ends_where_the_answer_starts():
    assert construire_prompt("triage", CAS).endswith("Réponse :\n")
    assert construire_prompt("qa", CAS).endswith("Réponse :\n")


def test_few_shot_examples_come_before_the_case():
    exemple = ("Femme de 30 ans, entorse de cheville.", '{"urgency_level": "deferred"}')
    prompt = construire_prompt("triage", CAS, exemples=[exemple])
    assert prompt.index(exemple[0]) < prompt.index(exemple[1]) < prompt.index(CAS)
    assert prompt.endswith(f"Cas : {CAS}\n\nRéponse :\n")


def test_prompt_without_examples_unchanged():
    # le prompt d'entraînement ne doit pas bouger avec l'ajout des exemples
    assert construire_prompt("triage", CAS) == f"{CONSIGNE_TRIAGE}\n\nCas : {CAS}\n\nRéponse :\n"


def test_unknown_task_rejected():
    with pytest.raises(KeyError):
        construire_prompt("resume", CAS)
