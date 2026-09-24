"""Service FastAPI qui expose le modèle de triage via vLLM."""

import secrets
import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import APIKeyHeader
from starlette.concurrency import iterate_in_threadpool
from vllm import AsyncEngineArgs, AsyncLLMEngine, SamplingParams
from vllm.utils import random_uuid

from app.config import (
    API_KEY, CHEMIN_MODELE, DTYPE, GPU_MEMORY_UTILIZATION, MAX_MODEL_LEN,
    PARAMETRES_DECODAGE,
)
from app.database import Base, SessionLocale, moteur
from app.models import Interaction, Log
from app.schemas import ReponseTriage, RequeteTriage

moteurs = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not API_KEY:
        raise RuntimeError("API_KEY n'est pas défini, l'API refuse de démarrer sans clé")
    args = AsyncEngineArgs(
        model=CHEMIN_MODELE, dtype=DTYPE,
        gpu_memory_utilization=GPU_MEMORY_UTILIZATION, max_model_len=MAX_MODEL_LEN,
    )
    moteurs["llm"] = AsyncLLMEngine.from_engine_args(args)
    async with moteur.begin() as connexion:
        await connexion.run_sync(Base.metadata.create_all)
    yield
    moteurs.clear()


app = FastAPI(title="Agent de triage CHSA", lifespan=lifespan)

entete_cle = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verifier_cle(cle: str | None = Depends(entete_cle)):
    # compare_digest évite de laisser deviner la clé au temps de réponse.
    if cle is None or not secrets.compare_digest(cle, API_KEY):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.middleware("http")
async def journaliser_requetes(request: Request, call_next):
    debut = time.perf_counter()
    reponse = await call_next(request)
    duree_ms = (time.perf_counter() - debut) * 1000

    detail_erreur = None
    if reponse.status_code >= 400:
        corps = b"".join([section async for section in reponse.body_iterator])
        reponse.body_iterator = iterate_in_threadpool(iter([corps]))
        detail_erreur = corps.decode(errors="replace")

    async with SessionLocale() as session:
        session.add(Log(
            method=request.method,
            path=request.url.path,
            status_code=reponse.status_code,
            total_time_ms=duree_ms,
            interaction_id=getattr(request.state, "interaction_id", None),
            error_detail=detail_erreur,
        ))
        await session.commit()

    return reponse


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/triage", response_model=ReponseTriage, dependencies=[Depends(verifier_cle)])
async def triage(requete: RequeteTriage, request: Request) -> ReponseTriage:
    params = SamplingParams(**PARAMETRES_DECODAGE)
    id_requete = random_uuid()

    debut_generation = time.perf_counter()
    sortie_finale = None
    async for sortie in moteurs["llm"].generate(requete.instruction, params, id_requete):
        sortie_finale = sortie
    duree_generation_ms = (time.perf_counter() - debut_generation) * 1000
    if sortie_finale is None:
        raise HTTPException(status_code=500, detail="The model returned no output")
    reponse = sortie_finale.outputs[0].text

    async with SessionLocale() as session:
        interaction = Interaction(
            instruction=requete.instruction, response=reponse,
            generation_time_ms=duree_generation_ms,
        )
        session.add(interaction)
        await session.commit()
        request.state.interaction_id = interaction.id

    return ReponseTriage(response=reponse)
