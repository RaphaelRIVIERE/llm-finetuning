"""Schémas Pydantic de l'API de triage."""

from typing import Annotated

from pydantic import BaseModel, StringConstraints

from app.config import LONGUEUR_MAX_CAS
from app.triage import SortieTriage


class RequeteTriage(BaseModel):
    # Les espaces autour sont retirés avant de vérifier la longueur : un texte fait
    # seulement d'espaces est refusé comme un texte vide.
    instruction: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=LONGUEUR_MAX_CAS)]


class ReponseTriage(SortieTriage):
    """Le JSON du modèle, validé, et l'id de l'interaction pour la retrouver en base."""

    interaction_id: int
