"""Entraînement SFT (LoRA) de Qwen3-1.7B-Base sur le dataset de triage médical."""

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path

import mlflow
import torch
from datasets import Dataset
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
from trl import SFTConfig, SFTTrainer

from app.prompts import construire_prompt
from scripts.suivi import enregistrer_debut_de_run, enregistrer_fin_de_run

DOSSIER_DATASET = Path("data/export/sft")


@dataclass
class Hyperparametres:
    """Config explicite du run SFT. Rien de ces valeurs ne doit être en dur ailleurs."""

    modele_base: str = "Qwen/Qwen3-1.7B-Base"
    seed: int = 42

    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: list = field(default_factory=lambda: [
        "q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj",
    ])

    max_length: int = 1024
    batch_size: int = 2
    gradient_accumulation_steps: int = 8
    epochs: float = 3.0
    learning_rate: float = 2e-4
    logging_steps: int = 10
    eval_steps: int = 50
    save_steps: int = 50

    dossier_sortie: str = "runs/sft"
    nom_experience_mlflow: str = "triage-chsa-sft"


def charger_dataset(split, taille_max=None, seed=42):
    """Charge un split JSONL du dataset SFT en colonnes prompt/completion. Le prompt est la
    consigne de la tâche suivie du texte, construit par la même fonction que l'API."""
    # Lu à la main plutôt qu'avec load_dataset("json") : une colonne vide sur les premières
    # milliers de lignes (transformations) reçoit un type vide, et le chargement plante à
    # la première valeur texte. On ne garde que les colonnes utiles à l'entraînement.
    with open(DOSSIER_DATASET / f"{split}.jsonl", encoding="utf-8") as f:
        dataset = Dataset.from_list([{c: ex[c] for c in ["tache", "instruction", "reponse"]} for ex in map(json.loads, f)])
    if taille_max is not None:
        # le fichier commence par tous les exemples de triage : on mélange avant de couper
        dataset = dataset.shuffle(seed=seed).select(range(min(taille_max, len(dataset))))
    dataset = dataset.map(lambda ex: {
        "prompt": construire_prompt(ex["tache"], ex["instruction"]),
        "completion": ex["reponse"],
    })
    return dataset.select_columns(["prompt", "completion"])


def entrainer(hp: Hyperparametres, nom_run: str, train_dataset, eval_dataset):
    set_seed(hp.seed)

    tokenizer = AutoTokenizer.from_pretrained(hp.modele_base)
    modele = AutoModelForCausalLM.from_pretrained(hp.modele_base, dtype=torch.bfloat16)

    peft_config = LoraConfig(
        r=hp.lora_r,
        lora_alpha=hp.lora_alpha,
        lora_dropout=hp.lora_dropout,
        target_modules=hp.lora_target_modules,
        task_type="CAUSAL_LM",
    )

    args = SFTConfig(
        output_dir=f"{hp.dossier_sortie}/{nom_run}",
        run_name=nom_run,
        seed=hp.seed,
        max_length=hp.max_length,
        per_device_train_batch_size=hp.batch_size,
        gradient_accumulation_steps=hp.gradient_accumulation_steps,
        num_train_epochs=hp.epochs,
        learning_rate=hp.learning_rate,
        bf16=True,
        gradient_checkpointing=True,
        logging_steps=hp.logging_steps,
        eval_strategy="steps",
        eval_steps=hp.eval_steps,
        save_strategy="steps",
        save_steps=hp.save_steps,
        # en fin de run, recharge le checkpoint qui a la plus petite loss de validation :
        # c'est lui qui est sauvegardé, pas le dernier
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        report_to=["mlflow"],
    )

    trainer = SFTTrainer(
        model=modele,
        args=args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        processing_class=tokenizer,
        peft_config=peft_config,
    )

    dossier_modele = Path(hp.dossier_sortie) / nom_run / "checkpoint_final"
    mlflow.set_experiment(hp.nom_experience_mlflow)
    with mlflow.start_run(run_name=nom_run):
        enregistrer_debut_de_run(hp, DOSSIER_DATASET, train_dataset, eval_dataset)
        resultat = trainer.train()
        trainer.save_model(str(dossier_modele))
        enregistrer_fin_de_run(trainer, resultat, dossier_modele)
    return trainer


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pilote", action="store_true",
        help="Run pilote sur un petit sous ensemble, pour valider que la pipeline tourne.",
    )
    parser.add_argument("--epochs", type=float, help="Nombre d'epochs, remplace la valeur de la config.")
    parser.add_argument("--nom-run", help="Nom du run, utilisé pour le dossier de sortie et MLflow.")
    args_cli = parser.parse_args()

    hp = Hyperparametres()
    if args_cli.epochs is not None:
        hp.epochs = args_cli.epochs

    if args_cli.pilote:
        hp.epochs = 1.0
        train_dataset = charger_dataset("train", taille_max=200, seed=hp.seed)
        eval_dataset = charger_dataset("validation", taille_max=50, seed=hp.seed)
        nom_run = "pilote"
    else:
        train_dataset = charger_dataset("train", seed=hp.seed)
        eval_dataset = charger_dataset("validation", seed=hp.seed)
        nom_run = "complet"

    if args_cli.nom_run is not None:
        nom_run = args_cli.nom_run

    entrainer(hp, nom_run, train_dataset, eval_dataset)
