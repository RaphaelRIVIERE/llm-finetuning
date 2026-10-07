"""Prépare un fichier pour relire à la main les réponses du modèle final sur le test.

On y met les urgences vitales ratées et un tirage de réponses correctes.

    uv run python -m scripts.relecture_securite
"""

import csv
import json
import random
from pathlib import Path

from app.triage import parser_sortie

FICHIER_REPONSES = Path("data/generations/test_sft_dpo.jsonl")
FICHIER_CAS = Path("data/export/sft/test.jsonl")
FICHIER_RELECTURE = Path("data/relecture/securite_test.csv")
NB_CORRECTS_PAR_LANGUE = 5

COLONNES = [
    "id", "langue", "groupe", "cas", "niveau_label", "niveau_modele", "specialite",
    "signes_alerte", "justification", "recommandation",
    # à remplir : oui ou non, et un commentaire libre
    "hallucination", "signe_gravite_oublie", "recommandation_dangereuse", "label_discutable",
    "commentaire",
]


def main(seed=42):
    # le fichier contient le travail de relecture : on ne l'écrase jamais
    if FICHIER_RELECTURE.exists():
        raise SystemExit(f"{FICHIER_RELECTURE} existe déjà, je ne l'écrase pas.")

    with open(FICHIER_CAS, encoding="utf-8") as f:
        cas = {e["id"]: e["instruction"] for e in map(json.loads, f) if e["tache"] == "triage"}
    with open(FICHIER_REPONSES, encoding="utf-8") as f:
        reponses = [json.loads(ligne) for ligne in f]

    rates, corrects = [], {"fr": [], "en": []}
    for reponse in reponses:
        sortie = parser_sortie(reponse["reponse_modele"]).sortie
        niveau = sortie.urgency_level.value if sortie else "invalide"
        if reponse["urgency_level"] == "maximum" and niveau != "maximum":
            rates.append((reponse, sortie, niveau, "urgence ratée"))
        elif sortie and niveau == reponse["urgency_level"]:
            corrects[reponse["langue"]].append((reponse, sortie, niveau, "correct"))

    rng = random.Random(seed)
    tirage = [ligne for langue in corrects for ligne in rng.sample(corrects[langue], NB_CORRECTS_PAR_LANGUE)]

    FICHIER_RELECTURE.parent.mkdir(parents=True, exist_ok=True)
    # point virgule et BOM : le fichier s'ouvre directement dans Excel ou LibreOffice en français
    with open(FICHIER_RELECTURE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLONNES, delimiter=";")
        writer.writeheader()
        for reponse, sortie, niveau, groupe in rates + tirage:
            writer.writerow({
                "id": reponse["id"],
                "langue": reponse["langue"],
                "groupe": groupe,
                "cas": cas[reponse["id"]],
                "niveau_label": reponse["urgency_level"],
                "niveau_modele": niveau,
                "specialite": sortie.specialty.value if sortie else "",
                "signes_alerte": " | ".join(sortie.red_flags) if sortie else "",
                "justification": sortie.justification if sortie else reponse["reponse_modele"][:500],
                "recommandation": sortie.recommendation if sortie else "",
            })
    print(f"{len(rates)} urgences ratées et {len(tirage)} réponses correctes dans {FICHIER_RELECTURE}")


if __name__ == "__main__":
    main()
