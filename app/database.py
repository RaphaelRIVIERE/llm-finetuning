"""Connexion à la base Postgres qui enregistre les questions et réponses."""

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import URL_BASE

moteur = create_async_engine(URL_BASE)
SessionLocale = async_sessionmaker(moteur, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
