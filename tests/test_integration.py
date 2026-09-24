"""Test de bout en bout contre l'API lancée pour de vrai avec le modèle final.

Demande un GPU, donc ignoré par défaut (et en CI). Pour le lancer, démarrer l'API puis :
API_URL=http://localhost:8000 uv run pytest tests/test_integration.py
"""

import os

import httpx
import pytest

API_URL = os.environ.get("API_URL")

pytestmark = pytest.mark.skipif(API_URL is None, reason="API_URL non défini, pas d'API réelle à appeler")


def test_douleur_thoracique_oriente_vers_le_coeur():
    # Urgence vitale typique, où un faux négatif serait le pire scénario pour un agent
    # de triage. Exemple 3 de docs/test_decodage_vllm_3.md, bien traité par le modèle.
    instruction = (
        "J'ai 58 ans, je fume, et j'ai une douleur dans la poitrine qui serre et qui "
        "descend dans le bras gauche depuis 30 minutes. Qu'est-ce que j'ai ?"
    )

    reponse = httpx.post(f"{API_URL}/triage", json={"instruction": instruction}, timeout=120)

    assert reponse.status_code == 200
    texte = reponse.json()["reponse"].lower()
    assert any(mot in texte for mot in ["myocard", "coronarien", "cardiaque", "infarctus"])
