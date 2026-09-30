"""Annotation des cas de triage par Mistral, en suivant le protocole de triage.

Pour l'instant : test sur un petit échantillon de cas MediQAl, à relire à la main.
"""

import argparse
import os
import random
import time
from collections import Counter
from pathlib import Path

import httpx
from dotenv import load_dotenv
from tqdm import tqdm

from app.triage import SortieTriage, Specialty, UrgencyLevel, parser_sortie
from scripts.cases import is_triage_case
from scripts.export import write_jsonl
from scripts.extraction import load_mediqal_cases

# Nom exact et pas "latest", pour que les labels restent reproductibles. Le nom renvoyé
# par l'API est aussi gardé avec chaque label.
MODELE = "mistral-large-2512"
URL_API = "https://api.mistral.ai/v1/chat/completions"
PROTOCOLE = Path("docs/protocole_triage.md")
DOSSIER_SORTIE = Path("data/annotation")
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

{protocole}"""


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
        # Le JSON attendu fait quelques centaines de tokens. Sans limite, la réponse
        # maximale possible peut compter dans les tokens par minute.
        "max_tokens": 1000,
        # Schéma imposé au décodage : les niveaux et spécialités ne peuvent pas sortir
        # des listes, ce que la consigne seule ne garantit pas.
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "sortie_triage", "schema": SortieTriage.model_json_schema(), "strict": True},
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=40, help="nombre de cas à annoter")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    load_dotenv()
    print("chargement et anonymisation des cas MediQAl...")
    cas_triage = [r for r in load_mediqal_cases() if is_triage_case(r["cas"], "fr")]
    echantillon = random.Random(args.seed).sample(cas_triage, args.n)
    consigne = construire_consigne()

    headers = {"Authorization": f"Bearer {os.environ['MISTRAL_API_KEY']}"}
    resultats = []
    with httpx.Client(headers=headers, timeout=60) as client:
        for record in tqdm(echantillon, desc="annotation"):
            texte, modele = annoter(client, consigne, record["cas"])
            parsing = parser_sortie(texte)
            resultats.append({
                "id": record["id"],
                "cas": record["cas"],
                "annotateur": modele,
                "reponse_brute": texte,
                "statut": parsing.statut.value,
                "sortie": parsing.sortie.model_dump(mode="json") if parsing.sortie else None,
            })
            time.sleep(PAUSE_SECONDES)

    chemin = DOSSIER_SORTIE / "test_annotateur.jsonl"
    write_jsonl(resultats, chemin)
    print(f"\nécrit dans {chemin}")
    print("statuts :", dict(Counter(r["statut"] for r in resultats)))
    print("niveaux :", dict(Counter(r["sortie"]["urgency_level"] for r in resultats if r["sortie"])))


if __name__ == "__main__":
    main()
