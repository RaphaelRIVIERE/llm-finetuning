"""Entraînement SFT (LoRA) de Qwen3-1.7B-Base sur le dataset de triage médical."""

import argparse
from dataclasses import dataclass, field
from pathlib import Path

import mlflow
import torch
from datasets import load_dataset
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
from trl import SFTConfig, SFTTrainer

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


def charger_dataset(split, taille_max=None):
    """Charge un split JSONL du dataset SFT et ne garde que les colonnes prompt/completion."""
    dataset = load_dataset("json", data_files=str(DOSSIER_DATASET / f"{split}.jsonl"), split="train")
    dataset = dataset.rename_columns({"instruction": "prompt", "reponse": "completion"})
    dataset = dataset.select_columns(["prompt", "completion"])
    if taille_max is not None:
        dataset = dataset.select(range(min(taille_max, len(dataset))))
    return dataset


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

    mlflow.set_experiment(hp.nom_experience_mlflow)
    with mlflow.start_run(run_name=nom_run):
        trainer.train()

    trainer.save_model(f"{hp.dossier_sortie}/{nom_run}/checkpoint_final")
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
        train_dataset = charger_dataset("train", taille_max=200)
        eval_dataset = charger_dataset("validation", taille_max=50)
        nom_run = "pilote"
    else:
        train_dataset = charger_dataset("train")
        eval_dataset = charger_dataset("validation")
        nom_run = "complet"

    if args_cli.nom_run is not None:
        nom_run = args_cli.nom_run

    entrainer(hp, nom_run, train_dataset, eval_dataset)
