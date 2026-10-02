"""Fusionne les adaptateurs SFT et DPO dans les poids de base : modèle final autonome pour
vLLM (génération des réponses du notebook 06, puis déploiement).

L'ordre suit l'entraînement : le DPO a été entraîné par dessus le modèle SFT fusionné,
donc on fusionne d'abord le SFT, puis le DPO.
"""

import argparse
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

MODELE_BASE = "Qwen/Qwen3-1.7B-Base"


def fusionner(checkpoint_sft, checkpoint_dpo, dossier_sortie):
    tokenizer = AutoTokenizer.from_pretrained(MODELE_BASE)
    base = AutoModelForCausalLM.from_pretrained(MODELE_BASE, dtype=torch.bfloat16).cuda()

    modele_sft = PeftModel.from_pretrained(base, checkpoint_sft).merge_and_unload()
    modele_final = PeftModel.from_pretrained(modele_sft, checkpoint_dpo).merge_and_unload()

    dossier_sortie.mkdir(parents=True, exist_ok=True)
    modele_final.save_pretrained(dossier_sortie)
    tokenizer.save_pretrained(dossier_sortie)
    print(f"Modèle fusionné (SFT {checkpoint_sft} + DPO {checkpoint_dpo}) sauvegardé dans {dossier_sortie}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sft", default="runs/sft/triage/checkpoint-600", help="adaptateur SFT")
    # checkpoint_final est le meilleur checkpoint du run, rechargé en fin d'entraînement
    parser.add_argument("--dpo", default="runs/dpo/triage/checkpoint_final", help="adaptateur DPO")
    parser.add_argument("--sortie", default="runs/final", type=Path, help="dossier du modèle fusionné")
    args = parser.parse_args()
    fusionner(args.sft, args.dpo, args.sortie)
