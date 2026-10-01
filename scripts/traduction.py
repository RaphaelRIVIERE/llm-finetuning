"""Traduction en anglais des champs texte des labels de triage des cas anglais.

À l'annotation, Mistral a écrit la justification et la recommandation en français pour
presque tous les cas anglais, et les `key_symptoms` à moitié en français. Ce script fait
traduire ces champs, sans envoyer ni le cas, ni le niveau, ni la spécialité : les labels
ne peuvent donc pas changer. Les traductions vont dans un fichier à part, chaque ligne
écrite dès qu'elle arrive : si le script s'arrête, on le relance et il reprend.
"""

import argparse
import hashlib
import json
import os
import time

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from tqdm import tqdm

from scripts.annotation import (
    ATTENTE_LIMITE_SECONDES, FICHIER_SORTIE, MODELE, PAUSE_SECONDES, URL_API, lire_annotations,
)
from scripts.cases import drop_short_vignettes
from scripts.extraction import FICHIER_TRADUCTIONS

CONSIGNE = """Tu traduis en anglais les champs d'un triage fait aux urgences. L'utilisateur envoie un objet JSON avec les clés key_symptoms, red_flags, justification et recommendation.

Réponds avec le même objet JSON, chaque texte traduit en anglais médical. Garde exactement le sens, n'ajoute rien et ne retire rien. Garde le même nombre d'éléments dans chaque liste, dans le même ordre. Si un texte est déjà en anglais, recopie le tel quel."""

CHAMPS = ["key_symptoms", "red_flags", "justification", "recommendation"]


class Traduction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key_symptoms: list[str]
    red_flags: list[str]
    justification: str = Field(min_length=1)
    recommendation: str = Field(min_length=1)


def traduire(client, champs):
    """Envoie les champs à Mistral. Renvoie le texte de sa réponse et le nom exact du modèle."""
    requete = {
        "model": MODELE,
        "temperature": 0,
        "random_seed": 42,
        "max_tokens": 1000,
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "traduction", "schema": Traduction.model_json_schema(), "strict": True},
        },
        "messages": [
            {"role": "system", "content": CONSIGNE},
            {"role": "user", "content": json.dumps(champs, ensure_ascii=False)},
        ],
    }
    reponse = client.post(URL_API, json=requete)
    if reponse.status_code == 429:
        time.sleep(ATTENTE_LIMITE_SECONDES)
        reponse = client.post(URL_API, json=requete)
    if reponse.is_error:
        raise RuntimeError(f"erreur {reponse.status_code} de l'API Mistral : {reponse.text}")
    corps = reponse.json()
    return corps["choices"][0]["message"]["content"], corps["model"]


def lire_traduction(texte, champs):
    """La traduction validée, ou None si le JSON est invalide ou si une liste n'a pas le
    même nombre d'éléments que l'original (un symptôme perdu ou ajouté)."""
    try:
        traduction = Traduction.model_validate_json(texte)
    except ValidationError:
        return None
    for nom in ["key_symptoms", "red_flags"]:
        if len(getattr(traduction, nom)) != len(champs[nom]):
            return None
    return traduction


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limite", type=int, default=None, help="ne traduire que les N premiers cas (test)")
    args = parser.parse_args()

    load_dotenv()
    cas_anglais = [
        r for r in drop_short_vignettes(lire_annotations(FICHIER_SORTIE))
        if r["langue"] == "en" and r["valide"]
    ]
    if args.limite:
        cas_anglais = cas_anglais[:args.limite]

    deja_faits = {r["id"] for r in lire_annotations(FICHIER_TRADUCTIONS)}
    a_traduire = [r for r in cas_anglais if r["id"] not in deja_faits]
    print(f"{len(deja_faits)} cas déjà traduits, {len(a_traduire)} à faire")

    version_prompt = hashlib.sha256(CONSIGNE.encode("utf-8")).hexdigest()[:12]

    headers = {"Authorization": f"Bearer {os.environ['MISTRAL_API_KEY']}"}
    with httpx.Client(headers=headers, timeout=60) as client, open(FICHIER_TRADUCTIONS, "a", encoding="utf-8") as f:
        for record in tqdm(a_traduire, desc="traduction"):
            debut = time.monotonic()
            champs = {nom: record["sortie"][nom] for nom in CHAMPS}
            texte, modele = traduire(client, champs)
            traduction = lire_traduction(texte, champs)
            resultat = {
                "id": record["id"],
                "traducteur": modele,
                "temperature": 0,
                "version_prompt": version_prompt,
                "reponse_brute": texte,
                "valide": traduction is not None,
                "traduction": traduction.model_dump() if traduction else None,
            }
            f.write(json.dumps(resultat, ensure_ascii=False) + "\n")
            f.flush()
            time.sleep(max(0, PAUSE_SECONDES - (time.monotonic() - debut)))

    traductions = lire_annotations(FICHIER_TRADUCTIONS)
    print(f"\n{len(traductions)} cas dans {FICHIER_TRADUCTIONS}")
    print("valides :", sum(r["valide"] for r in traductions))


if __name__ == "__main__":
    main()
