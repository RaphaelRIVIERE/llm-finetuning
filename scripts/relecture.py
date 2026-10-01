"""Prépare le fichier de relecture du test de triage : un cas par ligne, avec des colonnes
vides à remplir à la main.

La relecture se fait à l'aveugle : le fichier ne montre pas le label de Mistral, pour ne
pas influencer le relecteur. Les deux sont comparés ensuite par `id`, ce qui donne un taux
d'accord honnête.
"""

import csv
from pathlib import Path

from scripts.extraction import build_sft_dataset

FICHIER_RELECTURE = Path("data/relecture/test_triage.csv")
COLONNES = ["id", "langue", "cas", "niveau_relu", "specialite_relue", "commentaire"]


def main():
    # le fichier contient le travail de relecture : on ne l'écrase jamais
    if FICHIER_RELECTURE.exists():
        raise SystemExit(f"{FICHIER_RELECTURE} existe déjà, je ne l'écrase pas.")

    test = [e for e in build_sft_dataset() if e["tache"] == "triage" and e["split"] == "test"]
    test.sort(key=lambda e: (e["langue"] != "fr", e["id"]))

    FICHIER_RELECTURE.parent.mkdir(parents=True, exist_ok=True)
    # point virgule et BOM : le fichier s'ouvre directement dans Excel ou LibreOffice en français
    with open(FICHIER_RELECTURE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLONNES, delimiter=";")
        writer.writeheader()
        for exemple in test:
            writer.writerow({"id": exemple["id"], "langue": exemple["langue"], "cas": exemple["instruction"]})
    print(f"{len(test)} cas écrits dans {FICHIER_RELECTURE}")


if __name__ == "__main__":
    main()
