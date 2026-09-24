"""Configuration commune des tests de l'API.

vLLM demande un GPU et Postgres un serveur. On remplace le premier par un faux moteur
et le second par une base SQLite temporaire, pour que les tests tournent partout, y
compris sur les runners GitHub Actions qui n'ont pas de GPU.
"""

import os
import shutil
import sys
import tempfile
import types
import uuid
from types import SimpleNamespace

import pytest

from tests.constantes import REPONSE_FACTICE


class FauxMoteur:
    """Remplace AsyncLLMEngine : renvoie toujours la même réponse et garde les appels."""

    def __init__(self):
        self.appels = []
        # Passé à True par un test pour simuler un moteur qui ne produit aucune sortie.
        self.vide = False

    @classmethod
    def from_engine_args(cls, args):
        return cls()

    async def generate(self, prompt, params, request_id):
        self.appels.append(SimpleNamespace(prompt=prompt, params=params))
        if self.vide:
            return
        yield SimpleNamespace(outputs=[SimpleNamespace(text=REPONSE_FACTICE)])


# Tout ça doit être en place avant d'importer app.main : app.database crée le moteur
# SQLAlchemy à l'import, et app.main importe vllm.
DOSSIER_BASE = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{DOSSIER_BASE}/test.db"

faux_vllm = types.ModuleType("vllm")
faux_vllm.AsyncEngineArgs = lambda **kwargs: SimpleNamespace(**kwargs)
faux_vllm.AsyncLLMEngine = FauxMoteur
faux_vllm.SamplingParams = lambda **kwargs: SimpleNamespace(**kwargs)
faux_vllm_utils = types.ModuleType("vllm.utils")
faux_vllm_utils.random_uuid = lambda: uuid.uuid4().hex
sys.modules["vllm"] = faux_vllm
sys.modules["vllm.utils"] = faux_vllm_utils

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import select  # noqa: E402

from app.database import SessionLocale  # noqa: E402
from app.main import app, moteurs  # noqa: E402


@pytest.fixture(scope="session")
def client():
    # Un seul client pour toute la session : les connexions SQLite async restent
    # liées à la boucle d'événements du client qui les a ouvertes.
    with TestClient(app) as client:
        yield client
    shutil.rmtree(DOSSIER_BASE, ignore_errors=True)


@pytest.fixture
def faux_moteur(client):
    return moteurs["llm"]


@pytest.fixture
def lire_table(client):
    """Renvoie les lignes d'une table, dans la même boucle d'événements que l'API."""

    def lire(modele):
        async def requete():
            async with SessionLocale() as session:
                resultat = await session.execute(select(modele).order_by(modele.id))
                return resultat.scalars().all()

        return client.portal.call(requete)

    return lire
