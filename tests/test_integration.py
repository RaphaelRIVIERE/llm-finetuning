"""Test de bout en bout contre l'API lancée pour de vrai avec le modèle final.

Demande un GPU, donc ignoré par défaut (et en CI). Pour le lancer, démarrer l'API puis :
API_URL=http://localhost:8000 uv run pytest tests/test_integration.py
La clé API est lue dans le .env à la racine du projet.
"""

import os
from pathlib import Path

import httpx
import pytest
from dotenv import dotenv_values

API_URL = os.environ.get("API_URL")
# Lue dans le fichier et pas dans os.environ : conftest.py y met une fausse clé pour les
# tests unitaires, avant que ce module soit importé.
API_KEY = dotenv_values(Path(__file__).parent.parent / ".env").get("API_KEY")

pytestmark = pytest.mark.skipif(API_URL is None, reason="API_URL non défini, pas d'API réelle à appeler")


def test_douleur_thoracique_oriente_vers_le_coeur():
    # Urgence vitale typique, où un faux négatif serait le pire scénario pour un agent
    # de triage. Exemple 3 de docs/test_decodage_vllm_3.md, bien traité par le modèle.
    instruction = (
        "J'ai 58 ans, je fume, et j'ai une douleur dans la poitrine qui serre et qui "
        "descend dans le bras gauche depuis 30 minutes. Qu'est-ce que j'ai ?"
    )

    reponse = httpx.post(
        f"{API_URL}/triage", json={"instruction": instruction},
        headers={"X-API-Key": API_KEY}, timeout=120,
    )

    assert reponse.status_code == 200
    texte = reponse.json()["response"].lower()
    assert any(mot in texte for mot in ["myocard", "coronarien", "cardiaque", "infarctus"])
