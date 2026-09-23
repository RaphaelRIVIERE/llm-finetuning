"""Fusionne les adaptateurs SFT et DPO dans les poids de base : modèle final autonome pour le déploiement vLLM."""

from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

MODELE_BASE = "Qwen/Qwen3-1.7B-Base"
CHECKPOINT_SFT = "runs/sft/complet/checkpoint-500"
CHECKPOINT_DPO = "runs/dpo/complet/checkpoint-250"
DOSSIER_SORTIE = Path("runs/final")


def fusionner():
    tokenizer = AutoTokenizer.from_pretrained(MODELE_BASE)
    base = AutoModelForCausalLM.from_pretrained(MODELE_BASE, dtype=torch.bfloat16).cuda()

    modele_sft = PeftModel.from_pretrained(base, CHECKPOINT_SFT).merge_and_unload()
    modele_final = PeftModel.from_pretrained(modele_sft, CHECKPOINT_DPO).merge_and_unload()

    DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)
    modele_final.save_pretrained(DOSSIER_SORTIE)
    tokenizer.save_pretrained(DOSSIER_SORTIE)
    print(f"Modèle final fusionné (SFT {CHECKPOINT_SFT} + DPO {CHECKPOINT_DPO}) sauvegardé dans {DOSSIER_SORTIE}")


if __name__ == "__main__":
    fusionner()
