"""Comparaison avant / après DPO sur eval_clinique : mêmes exemples, deux générations."""

from pathlib import Path

import torch
from datasets import load_dataset
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

MODELE_BASE = "Qwen/Qwen3-1.7B-Base"
CHECKPOINT_SFT = "runs/sft/complet/checkpoint-500"
CHECKPOINT_DPO = "runs/dpo/complet/checkpoint-250"
DOSSIER_DATASET = Path("data/export/sft")
RAPPORT_MD = Path("docs/evaluation_dpo.md")
MAX_NOUVEAUX_TOKENS = 256
REPETITION_PENALTY = 1.3
NO_REPEAT_NGRAM_SIZE = 3
N_FRANCAIS = 5
N_ANGLAIS = 5


def charger_modele_sft_fusionne():
    tokenizer = AutoTokenizer.from_pretrained(MODELE_BASE)
    base = AutoModelForCausalLM.from_pretrained(MODELE_BASE, dtype=torch.bfloat16).cuda()
    modele_sft = PeftModel.from_pretrained(base, CHECKPOINT_SFT).merge_and_unload()
    return modele_sft, tokenizer


def generer(modele, tokenizer, exemples):
    resultats = []
    for exemple in exemples:
        encodage = tokenizer(exemple["instruction"], return_tensors="pt").to(modele.device)
        with torch.no_grad():
            sortie = modele.generate(
                **encodage, max_new_tokens=MAX_NOUVEAUX_TOKENS, do_sample=False,
                repetition_penalty=REPETITION_PENALTY, no_repeat_ngram_size=NO_REPEAT_NGRAM_SIZE,
                pad_token_id=tokenizer.eos_token_id,
            )
        generation = tokenizer.decode(sortie[0, encodage["input_ids"].shape[1]:], skip_special_tokens=True)
        resultats.append(generation)
    return resultats


def selectionner_exemples(dataset, langue, n):
    sous_ensemble = dataset.filter(lambda ex: ex["langue"] == langue)
    return sous_ensemble.select(range(min(n, len(sous_ensemble))))


def ecrire_rapport_md(exemples, avant, apres, chemin=RAPPORT_MD):
    lignes = [
        "# Évaluation DPO : avant / après",
        "",
        f"Avant : `{CHECKPOINT_SFT}` (SFT seul). Après : `{CHECKPOINT_DPO}` (SFT + DPO).",
        "",
        f"Génération avec repetition_penalty={REPETITION_PENALTY}, no_repeat_ngram_size={NO_REPEAT_NGRAM_SIZE}.",
        "",
    ]
    for i, (exemple, av, ap) in enumerate(zip(exemples, avant, apres), start=1):
        lignes += [
            f"## Exemple {i} ({exemple['langue']})",
            "",
            "**Instruction**",
            "",
            exemple["instruction"],
            "",
            "**Réponse attendue**",
            "",
            exemple["reponse"],
            "",
            "**Avant DPO (SFT seul)**",
            "",
            av,
            "",
            "**Après DPO**",
            "",
            ap,
            "",
        ]
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text("\n".join(lignes), encoding="utf-8")
    print(f"Rapport écrit dans {chemin}")


if __name__ == "__main__":
    eval_clinique = load_dataset("json", data_files=str(DOSSIER_DATASET / "eval_clinique.jsonl"), split="train")
    exemples_fr = selectionner_exemples(eval_clinique, "fr", N_FRANCAIS)
    exemples_en = selectionner_exemples(eval_clinique, "en", N_ANGLAIS)
    exemples = list(exemples_fr) + list(exemples_en)

    modele, tokenizer = charger_modele_sft_fusionne()

    print("Génération avant DPO (SFT seul)...")
    avant = generer(modele, tokenizer, exemples)

    print("Chargement de l'adaptateur DPO...")
    modele_dpo = PeftModel.from_pretrained(modele, CHECKPOINT_DPO)

    print("Génération après DPO...")
    apres = generer(modele_dpo, tokenizer, exemples)

    ecrire_rapport_md(exemples, avant, apres)
