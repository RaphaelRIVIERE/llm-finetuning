"""Évaluation de base du modèle SFT : perplexité sur le split test, générations sur eval_clinique."""

import math
from pathlib import Path

import torch
from datasets import load_dataset
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

MODELE_BASE = "Qwen/Qwen3-1.7B-Base"
CHECKPOINT = "runs/sft/complet/checkpoint-500"
DOSSIER_DATASET = Path("data/export/sft")
RAPPORT_MD = Path("docs/evaluation_sft.md")
MAX_LENGTH = 1024
N_GENERATIONS = 5
MAX_NOUVEAUX_TOKENS = 256
REPETITION_PENALTY = 1.3
NO_REPEAT_NGRAM_SIZE = 3


def charger_modele(checkpoint=CHECKPOINT):
    tokenizer = AutoTokenizer.from_pretrained(MODELE_BASE)
    base = AutoModelForCausalLM.from_pretrained(MODELE_BASE, dtype=torch.bfloat16).cuda()
    modele = PeftModel.from_pretrained(base, checkpoint)
    modele.eval()
    return modele, tokenizer


def perte_completion(modele, tokenizer, prompt, completion):
    """Loss sur les tokens de la réponse uniquement, prompt masqué (même logique que l'entraînement)."""
    tokens_prompt = tokenizer(prompt, add_special_tokens=False)["input_ids"]
    texte_complet = prompt + completion
    encodage = tokenizer(
        texte_complet, add_special_tokens=False, truncation=True, max_length=MAX_LENGTH, return_tensors="pt",
    ).to(modele.device)

    labels = encodage["input_ids"].clone()
    n_tokens_prompt = min(len(tokens_prompt), labels.shape[1])
    labels[0, :n_tokens_prompt] = -100

    n_tokens_completion = (labels != -100).sum().item()
    if n_tokens_completion == 0:
        return None

    with torch.no_grad():
        sortie = modele(**encodage, labels=labels)
    return sortie.loss.item(), n_tokens_completion


def evaluer_perplexite(modele, tokenizer, dataset):
    perte_totale = 0.0
    tokens_totaux = 0
    for exemple in dataset:
        resultat = perte_completion(modele, tokenizer, exemple["instruction"], exemple["reponse"])
        if resultat is None:
            continue
        loss, n_tokens = resultat
        perte_totale += loss * n_tokens
        tokens_totaux += n_tokens
    loss_moyenne = perte_totale / tokens_totaux
    return loss_moyenne, math.exp(loss_moyenne)


def generer_exemples(modele, tokenizer, dataset, n=N_GENERATIONS):
    resultats = []
    for exemple in dataset.select(range(n)):
        encodage = tokenizer(exemple["instruction"], return_tensors="pt").to(modele.device)
        with torch.no_grad():
            sortie = modele.generate(
                **encodage, max_new_tokens=MAX_NOUVEAUX_TOKENS, do_sample=False,
                repetition_penalty=REPETITION_PENALTY, no_repeat_ngram_size=NO_REPEAT_NGRAM_SIZE,
                pad_token_id=tokenizer.eos_token_id,
            )
        generation = tokenizer.decode(sortie[0, encodage["input_ids"].shape[1]:], skip_special_tokens=True)
        resultats.append({
            "instruction": exemple["instruction"],
            "reponse_attendue": exemple["reponse"],
            "reponse_generee": generation,
        })
        print("--- Instruction ---")
        print(exemple["instruction"])
        print("--- Réponse attendue ---")
        print(exemple["reponse"])
        print("--- Réponse générée ---")
        print(generation)
        print()
    return resultats


def ecrire_rapport_md(checkpoint, loss_moyenne, perplexite, n_test, generations, chemin=RAPPORT_MD):
    lignes = [
        "# Évaluation SFT",
        "",
        f"Checkpoint évalué : `{checkpoint}`",
        "",
        f"Perplexité sur le split test ({n_test} exemples) : {perplexite:.2f} (loss moyenne {loss_moyenne:.4f})",
        "",
        f"Génération avec repetition_penalty={REPETITION_PENALTY}, no_repeat_ngram_size={NO_REPEAT_NGRAM_SIZE}.",
        "",
        "## Exemples sur eval_clinique",
        "",
    ]
    for i, res in enumerate(generations, start=1):
        lignes += [
            f"### Exemple {i}",
            "",
            "**Instruction**",
            "",
            res["instruction"],
            "",
            "**Réponse attendue**",
            "",
            res["reponse_attendue"],
            "",
            "**Réponse générée**",
            "",
            res["reponse_generee"],
            "",
        ]
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text("\n".join(lignes), encoding="utf-8")
    print(f"Rapport écrit dans {chemin}")


if __name__ == "__main__":
    modele, tokenizer = charger_modele()

    test = load_dataset("json", data_files=str(DOSSIER_DATASET / "test.jsonl"), split="train")
    loss_moyenne, perplexite = evaluer_perplexite(modele, tokenizer, test)
    print(f"Split test ({len(test)} exemples) : loss moyenne = {loss_moyenne:.4f}, perplexité = {perplexite:.2f}")
    print()

    eval_clinique = load_dataset("json", data_files=str(DOSSIER_DATASET / "eval_clinique.jsonl"), split="train")
    generations = generer_exemples(modele, tokenizer, eval_clinique)

    ecrire_rapport_md(CHECKPOINT, loss_moyenne, perplexite, len(test), generations)
