"""Annotation des cas de triage par Mistral, en suivant le protocole de triage.

Annote tous les cas français et un tirage de vignettes anglaises. Chaque label est
écrit dans le fichier dès qu'il arrive : si le script s'arrête, on le relance et il
reprend là où il en était.
"""

import argparse
import hashlib
import json
import os
import random
import time
from collections import Counter
from pathlib import Path

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, ValidationError
from tqdm import tqdm

from app.triage import SortieTriage, Specialty, UrgencyLevel
from scripts.extraction import load_triage_cases

# Nom exact et pas "latest", pour que les labels restent reproductibles. Le nom renvoyé
# par l'API est aussi gardé avec chaque label.
MODELE = "mistral-large-2512"
URL_API = "https://api.mistral.ai/v1/chat/completions"
PROTOCOLE = Path("docs/protocole_triage.md")
FICHIER_SORTIE = Path("data/annotation/annotations.jsonl")
# Limite de Large : 1 requête par seconde. Si elle est quand même dépassée, on attend
# une minute avant de réessayer.
PAUSE_SECONDES = 1.1
ATTENTE_LIMITE_SECONDES = 60

CONSIGNE = """Tu fais le triage des patients à l'accueil des urgences. Applique le protocole ci dessous au cas donné par l'utilisateur.

Réponds uniquement avec un objet JSON qui a exactement ces clés, dans cet ordre :
- "urgency_level" : une valeur parmi {niveaux}
- "specialty" : une valeur parmi {specialites}
- "key_symptoms" : liste de chaînes courtes
- "red_flags" : liste de chaînes courtes, vide s'il n'y en a pas
- "justification" : 2 ou 3 phrases, dans la langue du cas
- "recommendation" : une phrase courte, dans la langue du cas
- "antecedents" : liste de chaînes courtes, vide s'il n'y en a pas
- "constantes_vitales" : objet avec les clés fc, pa, fr, spo2, temperature, null quand la valeur n'est pas dans le cas

{protocole}"""


class ConstantesVitales(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fc: str | None
    pa: str | None
    fr: str | None
    spo2: str | None
    temperature: str | None


class SortieAnnotation(SortieTriage):
    """Sortie de triage, plus les métadonnées extraites du cas. Ces deux champs
    remplissent le dataset, le modèle entraîné ne les produit pas."""

    antecedents: list[str]
    constantes_vitales: ConstantesVitales


def construire_consigne():
    return CONSIGNE.format(
        niveaux=", ".join(niveau.value for niveau in UrgencyLevel),
        specialites=", ".join(specialite.value for specialite in Specialty),
        protocole=PROTOCOLE.read_text(encoding="utf-8"),
    )


def annoter(client, consigne, cas):
    """Envoie un cas à Mistral. Renvoie le texte de sa réponse et le nom exact du modèle."""
    requete = {
        "model": MODELE,
        "temperature": 0,
        "random_seed": 42,
        # Le JSON attendu fait quelques centaines de tokens. Sans limite, la réponse
        # maximale possible peut compter dans les tokens par minute.
        "max_tokens": 1000,
        # Schéma imposé au décodage : les niveaux et spécialités ne peuvent pas sortir
        # des listes, ce que la consigne seule ne garantit pas.
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "sortie_annotation", "schema": SortieAnnotation.model_json_schema(), "strict": True},
        },
        "messages": [
            {"role": "system", "content": consigne},
            {"role": "user", "content": cas},
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


def lire_annotations(chemin):
    if not chemin.exists():
        return []
    with open(chemin, encoding="utf-8") as f:
        return [json.loads(ligne) for ligne in f]


def choisir_cas(n_anglais, seed):
    """Tous les cas français, et un tirage de `n_anglais` vignettes anglaises."""
    cas = load_triage_cases()
    francais = [r for r in cas if r["langue"] == "fr"]
    anglais = [r for r in cas if r["langue"] == "en"]
    return francais + random.Random(seed).sample(anglais, n_anglais)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-anglais", type=int, default=3300, help="nombre de vignettes anglaises à annoter")
    parser.add_argument("--limite", type=int, default=None, help="n'annoter que les N premiers cas (test)")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    load_dotenv()
    print("chargement des cas de triage...")
    a_annoter = choisir_cas(args.n_anglais, args.seed)
    if args.limite:
        a_annoter = a_annoter[:args.limite]

    deja_faits = {r["id"] for r in lire_annotations(FICHIER_SORTIE)}
    a_annoter = [r for r in a_annoter if r["id"] not in deja_faits]
    print(f"{len(deja_faits)} cas déjà annotés, {len(a_annoter)} à faire")

    consigne = construire_consigne()
    # Version du prompt : si la consigne ou le protocole change, elle change aussi
    version_prompt = hashlib.sha256(consigne.encode("utf-8")).hexdigest()[:12]

    FICHIER_SORTIE.parent.mkdir(parents=True, exist_ok=True)
    headers = {"Authorization": f"Bearer {os.environ['MISTRAL_API_KEY']}"}
    with httpx.Client(headers=headers, timeout=60) as client, open(FICHIER_SORTIE, "a", encoding="utf-8") as f:
        for record in tqdm(a_annoter, desc="annotation"):
            debut = time.monotonic()
            texte, modele = annoter(client, consigne, record["cas"])
            try:
                annotation = SortieAnnotation.model_validate_json(texte)
            except ValidationError:
                annotation = None
            if annotation:
                # Malgré le protocole, Mistral met parfois un mot (« hyperthermique ») au
                # lieu d'un chiffre : on ne garde que les valeurs chiffrées
                for nom, valeur in annotation.constantes_vitales:
                    if valeur and not any(c.isdigit() for c in valeur):
                        setattr(annotation.constantes_vitales, nom, None)
            resultat = {
                **record,
                "annotateur": modele,
                "temperature": 0,
                "version_prompt": version_prompt,
                "reponse_brute": texte,
                "valide": annotation is not None,
                "sortie": annotation.model_dump(mode="json", exclude={"antecedents", "constantes_vitales"}) if annotation else None,
                "antecedents": annotation.antecedents if annotation else [],
                "constantes_vitales": annotation.constantes_vitales.model_dump() if annotation else {},
            }
            f.write(json.dumps(resultat, ensure_ascii=False) + "\n")
            f.flush()
            # Un appel prend souvent plus d'une seconde : on n'attend que le reste
            time.sleep(max(0, PAUSE_SECONDES - (time.monotonic() - debut)))

    annotations = lire_annotations(FICHIER_SORTIE)
    print(f"\n{len(annotations)} cas dans {FICHIER_SORTIE}")
    print("valides :", sum(r["valide"] for r in annotations))
    print("niveaux :", dict(Counter((r["langue"], r["sortie"]["urgency_level"]) for r in annotations if r["valide"])))


if __name__ == "__main__":
    main()
