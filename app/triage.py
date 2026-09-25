"""Format JSON de la sortie de triage : modèle Pydantic, écriture et parsing."""

import json
from dataclasses import dataclass
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class UrgencyLevel(StrEnum):
    MAXIMUM = "maximum"
    MODERATE = "moderate"
    DEFERRED = "deferred"


class Specialty(StrEnum):
    CARDIOLOGY = "cardiology"
    NEUROLOGY = "neurology"
    PULMONOLOGY = "pulmonology"
    GASTROENTEROLOGY = "gastroenterology"
    TRAUMA_ORTHOPEDICS = "trauma_orthopedics"
    OBSTETRICS_GYNECOLOGY = "obstetrics_gynecology"
    PSYCHIATRY = "psychiatry"
    INFECTIOUS_DISEASES = "infectious_diseases"
    NEPHROLOGY_UROLOGY = "nephrology_urology"
    GENERAL_MEDICINE = "general_medicine"


class SortieTriage(BaseModel):
    # L'ordre des champs fixe l'ordre des clés dans le JSON d'entraînement.
    # urgency_level vient en premier : c'est la première valeur générée. Pour son
    # score, on force le préfixe {"urgency_level": " et on lit le token qui suit.
    model_config = ConfigDict(extra="forbid")

    urgency_level: UrgencyLevel
    specialty: Specialty
    key_symptoms: list[str] = Field(min_length=1)
    # Peut être vide, surtout pour un cas deferred.
    red_flags: list[str]
    justification: str = Field(min_length=1)


def vers_json(sortie: SortieTriage) -> str:
    """Écrit la sortie en JSON, toujours au même format (accents gardés tels quels)."""
    return json.dumps(sortie.model_dump(mode="json"), ensure_ascii=False)


class StatutParsing(StrEnum):
    VALIDE = "valide"
    # Pas de JSON lisible dans le texte.
    JSON_INVALIDE = "json_invalide"
    # JSON lisible mais clé manquante, clé en trop, mauvais type ou champ vide.
    SCHEMA_INVALIDE = "schema_invalide"
    # Toutes les clés sont là mais un niveau ou une spécialité sort des listes.
    VALEUR_HORS_LISTE = "valeur_hors_liste"


@dataclass
class ResultatParsing:
    statut: StatutParsing
    sortie: SortieTriage | None = None


def extraire_json(texte: str) -> dict | None:
    """Renvoie le premier objet JSON trouvé dans le texte, ou None.

    Le modèle peut entourer le JSON de texte ou d'un bloc ```json. On essaie de lire
    un objet à partir de chaque accolade ouvrante, et on garde le premier qui passe.
    """
    decodeur = json.JSONDecoder()
    debut = texte.find("{")
    while debut != -1:
        try:
            objet, _ = decodeur.raw_decode(texte, debut)
        except json.JSONDecodeError:
            pass
        else:
            if isinstance(objet, dict):
                return objet
        debut = texte.find("{", debut + 1)
    return None


def parser_sortie(texte: str) -> ResultatParsing:
    """Extrait, charge et valide la sortie du modèle."""
    objet = extraire_json(texte)
    if objet is None:
        return ResultatParsing(StatutParsing.JSON_INVALIDE)

    try:
        sortie = SortieTriage.model_validate(objet)
    except ValidationError as erreur:
        # Hors liste seulement si toutes les erreurs viennent d'un Enum. Dès qu'il y
        # a aussi un problème de structure, c'est une erreur de schéma.
        types_erreurs = {e["type"] for e in erreur.errors()}
        if types_erreurs == {"enum"}:
            return ResultatParsing(StatutParsing.VALEUR_HORS_LISTE)
        return ResultatParsing(StatutParsing.SCHEMA_INVALIDE)

    return ResultatParsing(StatutParsing.VALIDE, sortie)
