"""Service FastAPI qui expose le modèle de triage via vLLM."""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from starlette.concurrency import iterate_in_threadpool
from vllm import AsyncEngineArgs, AsyncLLMEngine, SamplingParams
from vllm.utils import random_uuid

from app.config import (
    CHEMIN_MODELE, GPU_MEMORY_UTILIZATION, MAX_MODEL_LEN, PARAMETRES_DECODAGE,
)
from app.database import Base, SessionLocale, moteur
from app.models import Interaction, Log
from app.schemas import ReponseTriage, RequeteTriage

moteurs = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    args = AsyncEngineArgs(
        model=CHEMIN_MODELE, dtype="bfloat16",
        gpu_memory_utilization=GPU_MEMORY_UTILIZATION, max_model_len=MAX_MODEL_LEN,
    )
    moteurs["llm"] = AsyncLLMEngine.from_engine_args(args)
    async with moteur.begin() as connexion:
        await connexion.run_sync(Base.metadata.create_all)
    yield
    moteurs.clear()


app = FastAPI(title="Agent de triage CHSA", lifespan=lifespan)


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


@app.get("/sante")
async def sante():
    return {"statut": "ok"}


@app.post("/triage", response_model=ReponseTriage)
async def triage(requete: RequeteTriage, request: Request) -> ReponseTriage:
    params = SamplingParams(**PARAMETRES_DECODAGE)
    id_requete = random_uuid()

    debut_generation = time.perf_counter()
    sortie_finale = None
    async for sortie in moteurs["llm"].generate(requete.instruction, params, id_requete):
        sortie_finale = sortie
    duree_generation_ms = (time.perf_counter() - debut_generation) * 1000
    if sortie_finale is None:
        raise HTTPException(status_code=500, detail="Le modèle n'a renvoyé aucune sortie")
    reponse = sortie_finale.outputs[0].text

    async with SessionLocale() as session:
        interaction = Interaction(
            instruction=requete.instruction, response=reponse,
            generation_time_ms=duree_generation_ms,
        )
        session.add(interaction)
        await session.commit()
        request.state.interaction_id = interaction.id

    return ReponseTriage(reponse=reponse)
