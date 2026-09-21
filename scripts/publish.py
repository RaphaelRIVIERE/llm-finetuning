"""Publie le dataset exporté (voir scripts/export.py) sur Hugging Face Hub."""

import os
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import HfApi

REPO_ID = "rriviere/oc-llm-finetuning-dataset"
DOSSIER_EXPORT = Path("data/export")


def publish(repo_id=REPO_ID, dossier_export=DOSSIER_EXPORT, private=False):
    load_dotenv()
    api = HfApi(token=os.environ["HF_TOKEN_WRITE"])
    api.create_repo(repo_id=repo_id, repo_type="dataset", private=private, exist_ok=True)
    api.upload_folder(
        repo_id=repo_id,
        repo_type="dataset",
        folder_path=dossier_export,
        allow_patterns=["*.jsonl", "README.md"],
        commit_message="Export du dataset SFT et DPO",
    )
    print(f"Publié : https://huggingface.co/datasets/{repo_id}")


if __name__ == "__main__":
    publish()
