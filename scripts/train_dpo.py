"""Alignement DPO (LoRA) du modèle SFT sur les paires de préférence UltraMedical-Preference."""

import argparse
from dataclasses import dataclass, field
from pathlib import Path

import mlflow
import torch
from datasets import load_dataset
from peft import LoraConfig, PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
from trl import DPOConfig, DPOTrainer

from app.prompts import construire_prompt
from scripts.suivi import enregistrer_debut_de_run, enregistrer_fin_de_run

MODELE_BASE = "Qwen/Qwen3-1.7B-Base"
CHECKPOINT_SFT = "runs/sft/complet/checkpoint-500"
DOSSIER_DATASET = Path("data/export/dpo")


@dataclass
class Hyperparametres:
    """Config explicite du run DPO. Rien de ces valeurs ne doit être en dur ailleurs."""

    seed: int = 42

    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: list = field(default_factory=lambda: [
        "q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj",
    ])

    # Plus élevé que le défaut TRL (0.1) : recommandation du mentor pour limiter la
    # dérive du modèle loin du SFT, notamment pour ne pas trop dégrader le français
    # alors que les paires de préférence sont entièrement en anglais.
    beta: float = 0.3

    max_length: int = 1024
    batch_size: int = 1
    eval_batch_size: int = 1
    gradient_accumulation_steps: int = 16
    epochs: float = 1.0
    learning_rate: float = 5e-5
    logging_steps: int = 10
    eval_steps: int = 50
    save_steps: int = 50

    dossier_sortie: str = "runs/dpo"
    nom_experience_mlflow: str = "triage-chsa-dpo"


def charger_dataset(split, taille_max=None, seed=42):
    """Charge un split JSONL du dataset DPO en colonnes prompt/chosen/rejected. Le prompt
    reçoit la consigne de sa tâche, comme au SFT."""
    dataset = load_dataset("json", data_files=str(DOSSIER_DATASET / f"{split}.jsonl"), split="train")
    if taille_max is not None:
        # tirage au hasard plutôt que les premières lignes, rangées dans l'ordre de la source
        dataset = dataset.shuffle(seed=seed).select(range(min(taille_max, len(dataset))))
    dataset = dataset.map(lambda ex: {"prompt": construire_prompt(ex["tache"], ex["prompt"])})
    return dataset.select_columns(["prompt", "chosen", "rejected"])


def charger_modele_sft_fusionne(checkpoint=CHECKPOINT_SFT):
    """Fusionne l'adaptateur LoRA du SFT dans les poids de base : c'est le point de
    départ du DPO. Le nouvel adaptateur LoRA du DPO s'entraîne par dessus ce modèle
    fusionné, qui sert aussi de modèle de référence (adaptateur DPO désactivé), sans
    charger un second modèle complet en mémoire."""
    base = AutoModelForCausalLM.from_pretrained(MODELE_BASE, dtype=torch.bfloat16)
    modele_sft = PeftModel.from_pretrained(base, checkpoint)
    return modele_sft.merge_and_unload()


def entrainer(hp: Hyperparametres, nom_run: str, train_dataset, eval_dataset):
    set_seed(hp.seed)

    tokenizer = AutoTokenizer.from_pretrained(MODELE_BASE)
    modele = charger_modele_sft_fusionne()

    peft_config = LoraConfig(
        r=hp.lora_r,
        lora_alpha=hp.lora_alpha,
        lora_dropout=hp.lora_dropout,
        target_modules=hp.lora_target_modules,
        task_type="CAUSAL_LM",
    )

    args = DPOConfig(
        output_dir=f"{hp.dossier_sortie}/{nom_run}",
        run_name=nom_run,
        seed=hp.seed,
        beta=hp.beta,
        max_length=hp.max_length,
        per_device_train_batch_size=hp.batch_size,
        per_device_eval_batch_size=hp.eval_batch_size,
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

    trainer = DPOTrainer(
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
        mlflow.log_param("checkpoint_sft", CHECKPOINT_SFT)
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
    parser.add_argument(
        "--taille-train", type=int, default=5000,
        help="Nombre de paires train utilisées (le split complet fait environ 63 000 paires).",
    )
    parser.add_argument(
        "--taille-eval", type=int, default=200,
        help="Nombre de paires de validation utilisées pendant l'entraînement (le split complet fait environ 7900 paires).",
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
        train_dataset = charger_dataset("train", taille_max=args_cli.taille_train, seed=hp.seed)
        eval_dataset = charger_dataset("validation", taille_max=args_cli.taille_eval, seed=hp.seed)
        nom_run = "complet"

    if args_cli.nom_run is not None:
        nom_run = args_cli.nom_run

    entrainer(hp, nom_run, train_dataset, eval_dataset)
