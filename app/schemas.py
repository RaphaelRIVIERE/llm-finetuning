"""Schémas Pydantic de l'API de triage."""

from pydantic import BaseModel


class RequeteTriage(BaseModel):
    instruction: str


class ReponseTriage(BaseModel):
    response: str
