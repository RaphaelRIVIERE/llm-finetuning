"""Fait répondre un modèle aux cas de triage d'un split, avec vLLM, et écrit ses réponses
brutes dans un fichier. Le notebook 06 les compare ensuite avec scripts/evaluation.py.

Un modèle est un modèle de base (nom Hugging Face ou dossier fusionné), avec ou sans
adaptateur LoRA. Exemples :

    # SFT : modèle de base + adaptateur du meilleur checkpoint
    python -m scripts.generation --nom sft --adaptateur runs/sft/triage/checkpoint-600

    # baseline : modèle de base seul, avec quelques exemples du train dans le prompt
    python -m scripts.generation --nom base_few_shot --few-shot 3
"""

import argparse
import json
import random
from pathlib import Path

from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest

from app.config import GPU_MEMORY_UTILIZATION, MAX_MODEL_LEN, PARAMETRES_DECODAGE
from app.prompts import construire_prompt
from app.triage import UrgencyLevel

MODELE_BASE = "Qwen/Qwen3-1.7B-Base"
DOSSIER_DATASET = Path("data/export/sft")
DOSSIER_SORTIE = Path("data/generations")
# Les exemples few shot sont choisis parmi les cas courts, pour garder un prompt court
LONGUEUR_MAX_EXEMPLE = 600

# Le même décodage que l'API (voir app/config.py). L'arrêt au retour à la ligne compte
# aussi pour le modèle de base, qui sinon continue avec un nouveau « Cas : » inventé.
DECODAGE = SamplingParams(**PARAMETRES_DECODAGE)


def lire_triage(split):
    """Les exemples de triage d'un split du dataset exporté."""
    with open(DOSSIER_DATASET / f"{split}.jsonl", encoding="utf-8") as f:
        exemples = [json.loads(ligne) for ligne in f]
    return [e for e in exemples if e["tache"] == "triage"]


def choisir_exemples(n, seed):
    """`n` exemples du train pour le few shot, en tournant sur les trois niveaux. Le train
    seulement : aucun cas évalué ne peut servir d'exemple."""
    rng = random.Random(seed)
    courts = [e for e in lire_triage("train") if len(e["instruction"]) <= LONGUEUR_MAX_EXEMPLE]
    niveaux = [niveau.value for niveau in UrgencyLevel]
    choisis = []
    for i in range(n):
        candidats = [e for e in courts if e["urgency_level"] == niveaux[i % len(niveaux)]]
        choisis.append(rng.choice(candidats))
    return [(e["instruction"], e["reponse"]) for e in choisis]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nom", required=True, help="nom du modèle, donne le nom du fichier de sortie")
    parser.add_argument("--modele", default=MODELE_BASE, help="modèle de base ou dossier d'un modèle fusionné")
    parser.add_argument("--adaptateur", default=None, help="dossier d'un adaptateur LoRA à appliquer")
    parser.add_argument("--few-shot", type=int, default=0, help="nombre d'exemples du train dans le prompt")
    parser.add_argument("--split", default="validation")
    parser.add_argument("--limite", type=int, default=None, help="ne faire que les N premiers cas (test)")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    cas = lire_triage(args.split)
    if args.limite:
        cas = cas[:args.limite]
    exemples = choisir_exemples(args.few_shot, args.seed) if args.few_shot else []
    prompts = [construire_prompt("triage", e["instruction"], exemples) for e in cas]

    llm = LLM(
        model=args.modele,
        dtype="bfloat16",
        gpu_memory_utilization=GPU_MEMORY_UTILIZATION,
        max_model_len=MAX_MODEL_LEN,
        seed=args.seed,
        enable_lora=args.adaptateur is not None,
        max_lora_rank=16,
    )
    lora = LoRARequest("adaptateur", 1, args.adaptateur) if args.adaptateur else None
    sorties = llm.generate(prompts, DECODAGE, lora_request=lora)

    DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)
    chemin = DOSSIER_SORTIE / f"{args.split}_{args.nom}.jsonl"
    with open(chemin, "w", encoding="utf-8") as f:
        for exemple, sortie in zip(cas, sorties):
            f.write(json.dumps({
                "id": exemple["id"],
                "langue": exemple["langue"],
                "urgency_level": exemple["urgency_level"],
                "reponse_modele": sortie.outputs[0].text,
                "modele": args.modele,
                "adaptateur": args.adaptateur,
                "few_shot": args.few_shot,
            }, ensure_ascii=False) + "\n")
    print(f"{len(cas)} réponses écrites dans {chemin}")


if __name__ == "__main__":
    main()
