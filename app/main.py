"""Service FastAPI qui expose le modèle de triage via vLLM."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from vllm import AsyncEngineArgs, AsyncLLMEngine, SamplingParams
from vllm.utils import random_uuid

from app.schemas import ReponseTriage, RequeteTriage

CHEMIN_MODELE = os.environ.get("CHEMIN_MODELE", "runs/final")
MAX_NOUVEAUX_TOKENS = 256
REPETITION_PENALTY = 1.3
# Défaut vLLM (~0.9) trop haut sur un GPU 8 Go partagé avec le reste du système (WSL).
GPU_MEMORY_UTILIZATION = float(os.environ.get("GPU_MEMORY_UTILIZATION", "0.8"))
# Défaut du modèle (32768) réserve plus de cache KV que ce qu'il reste de VRAM après
# le chargement des poids. Les instructions et réponses de triage sont courtes.
MAX_MODEL_LEN = int(os.environ.get("MAX_MODEL_LEN", "4096"))

moteurs = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    args = AsyncEngineArgs(
        model=CHEMIN_MODELE, dtype="bfloat16",
        gpu_memory_utilization=GPU_MEMORY_UTILIZATION, max_model_len=MAX_MODEL_LEN,
    )
    moteurs["llm"] = AsyncLLMEngine.from_engine_args(args)
    yield
    moteurs.clear()


app = FastAPI(title="Agent de triage CHSA", lifespan=lifespan)


@app.get("/sante")
async def sante():
    return {"statut": "ok"}


@app.post("/triage", response_model=ReponseTriage)
async def triage(requete: RequeteTriage) -> ReponseTriage:
    # repetition_penalty seul, vLLM n'a pas d'équivalent à no_repeat_ngram_size utilisé
    # pendant l'évaluation Transformers (voir docs/experimentations.md), à revalider.
    params = SamplingParams(
        max_tokens=MAX_NOUVEAUX_TOKENS,
        temperature=0.0,
        repetition_penalty=REPETITION_PENALTY,
    )
    id_requete = random_uuid()
    sortie_finale = None
    async for sortie in moteurs["llm"].generate(requete.instruction, params, id_requete):
        sortie_finale = sortie
    return ReponseTriage(reponse=sortie_finale.outputs[0].text)
