"""Connexion à la base Postgres qui enregistre les questions et réponses."""

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import URL_BASE

# Neon coupe les connexions quand la base se met en veille. pool_pre_ping teste la
# connexion avant usage et en rouvre une si elle a été fermée.
moteur = create_async_engine(URL_BASE, pool_pre_ping=True)
SessionLocale = async_sessionmaker(moteur, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
