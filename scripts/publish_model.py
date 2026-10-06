"""Publie le modèle fusionné (voir scripts/merge_model.py) et sa model card sur Hugging
Face Hub. Affiche la révision publiée : c'est elle qu'on fixe pour le déploiement."""

import os
import shutil
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import HfApi

REPO_ID = "rriviere/triage-chsa-qwen3-1.7b"
DOSSIER_MODELE = Path("runs/final")
MODEL_CARD = Path("docs/model_card.md")


def publish(repo_id=REPO_ID, dossier_modele=DOSSIER_MODELE, private=False):
    load_dotenv()
    # Hugging Face lit la card dans le README.md du dépôt
    shutil.copy(MODEL_CARD, dossier_modele / "README.md")

    api = HfApi(token=os.environ["HF_TOKEN_WRITE"])
    api.create_repo(repo_id=repo_id, repo_type="model", private=private, exist_ok=True)
    commit = api.upload_folder(
        repo_id=repo_id,
        repo_type="model",
        folder_path=dossier_modele,
        # retire du Hub les fichiers de l'ancien modèle qui n'existent plus en local
        delete_patterns=["*"],
        commit_message="Modèle SFT + DPO fusionné et model card",
    )
    print(f"Publié : https://huggingface.co/{repo_id}")
    print(f"Révision : {commit.oid}")


if __name__ == "__main__":
    publish()
