"""Connexion à la base Postgres qui enregistre les questions et réponses."""

import os

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

URL_BASE = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg://triage:triage@localhost:5432/triage"
)

moteur = create_async_engine(URL_BASE)
SessionLocale = async_sessionmaker(moteur, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
