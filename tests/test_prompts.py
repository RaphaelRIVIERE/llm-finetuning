"""Tests de la construction des prompts."""

import pytest

from app.prompts import construire_prompt
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


def test_unknown_task_rejected():
    with pytest.raises(KeyError):
        construire_prompt("resume", CAS)
