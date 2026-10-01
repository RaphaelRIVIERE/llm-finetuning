"""Traçabilité des entraînements dans MLflow, en plus de ce que Transformers enregistre
déjà (réglages d'entraînement, métriques, commit Git) : réglages LoRA, version du
dataset, GPU, durée et adaptateur LoRA du meilleur checkpoint."""

import hashlib
from pathlib import Path

import mlflow
import torch


def empreinte(chemin):
    """12 premiers caractères du SHA-256 d'un fichier : identifie la version exacte lue."""
    sha = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            sha.update(bloc)
    return sha.hexdigest()[:12]


def enregistrer_debut_de_run(hp, dossier_dataset, train_dataset, eval_dataset):
    """Réglages LoRA, fichiers du dataset lus et GPU utilisé."""
    mlflow.log_params({
        "lora_r": hp.lora_r,
        "lora_alpha": hp.lora_alpha,
        "lora_dropout": hp.lora_dropout,
        "lora_target_modules": ",".join(hp.lora_target_modules),
        "dataset_train_sha256": empreinte(dossier_dataset / "train.jsonl"),
        "dataset_validation_sha256": empreinte(dossier_dataset / "validation.jsonl"),
        "n_exemples_train": len(train_dataset),
        "n_exemples_validation": len(eval_dataset),
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
    })


def enregistrer_fin_de_run(trainer, resultat, dossier_modele):
    """Durée en heures GPU, meilleur checkpoint et adaptateur LoRA sauvegardé."""
    mlflow.log_metric("duree_heures_gpu", resultat.metrics["train_runtime"] / 3600)
    if trainer.state.best_model_checkpoint:
        mlflow.log_param("meilleur_checkpoint", Path(trainer.state.best_model_checkpoint).name)
        mlflow.log_metric("meilleure_eval_loss", trainer.state.best_metric)
    # l'adaptateur seul (quelques dizaines de Mo) : le modèle de base ne change pas
    mlflow.log_artifacts(str(dossier_modele), artifact_path="adaptateur_lora")
