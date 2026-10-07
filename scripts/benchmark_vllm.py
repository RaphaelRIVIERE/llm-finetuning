"""Compare vLLM et transformers.generate sur les mêmes cas, en local, pour justifier vLLM.

Mêmes cas et même décodage que scripts/benchmark_api.py. Chaque moteur est mesuré cas
par cas, puis sur tous les cas d'un coup. Un seul moteur par lancement, car les deux ne
tiennent pas ensemble dans la mémoire du GPU.

    uv run python -m scripts.benchmark_vllm --moteur vllm
    uv run python -m scripts.benchmark_vllm --moteur transformers
"""

import argparse
import json
import time
from pathlib import Path

from app.config import GPU_MEMORY_UTILIZATION, MAX_MODEL_LEN, PARAMETRES_DECODAGE
from app.prompts import construire_prompt
from scripts.benchmark_api import lire_cas

MODELE = "runs/final"
DOSSIER_SORTIE = Path("data/benchmark")


def couper(texte):
    """Garde le texte jusqu'au premier retour à la ligne, comme le stop de vLLM."""
    return texte.split("\n", 1)[0]


def moteur_vllm():
    from vllm import LLM, SamplingParams

    llm = LLM(model=MODELE, dtype="bfloat16", gpu_memory_utilization=GPU_MEMORY_UTILIZATION, max_model_len=MAX_MODEL_LEN)
    params = SamplingParams(**PARAMETRES_DECODAGE)

    def generer(prompts):
        return [sortie.outputs[0].text for sortie in llm.generate(prompts, params, use_tqdm=False)]

    return generer, llm.get_tokenizer()


def moteur_transformers(taille_lot):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    # Remplissage à gauche : en génération par lot, tous les prompts doivent finir au même
    # endroit pour que les nouveaux tokens soient alignés.
    tokenizer = AutoTokenizer.from_pretrained(MODELE, padding_side="left")
    modele = AutoModelForCausalLM.from_pretrained(MODELE, dtype=torch.bfloat16).cuda().eval()

    def generer_lot(prompts):
        entrees = tokenizer(prompts, return_tensors="pt", padding=True).to("cuda")
        with torch.no_grad():
            sorties = modele.generate(
                **entrees,
                max_new_tokens=PARAMETRES_DECODAGE["max_tokens"],
                do_sample=False,
                stop_strings=PARAMETRES_DECODAGE["stop"],
                tokenizer=tokenizer,
                pad_token_id=tokenizer.pad_token_id,
            )
        nouveaux = sorties[:, entrees["input_ids"].shape[1]:]
        return [couper(texte) for texte in tokenizer.batch_decode(nouveaux, skip_special_tokens=True)]

    def generer(prompts):
        textes = []
        for debut in range(0, len(prompts), taille_lot):
            textes += generer_lot(prompts[debut:debut + taille_lot])
        return textes

    return generer, tokenizer


def mesurer(generer, tokenizer, prompts, un_par_un):
    debut = time.perf_counter()
    if un_par_un:
        textes = [generer([prompt])[0] for prompt in prompts]
    else:
        textes = generer(prompts)
    duree_s = time.perf_counter() - debut
    # Les tokens sont recomptés sur le texte final, de la même façon pour les deux moteurs.
    nb_tokens = sum(len(tokenizer(texte)["input_ids"]) for texte in textes)
    resume = {
        "duree_s": round(duree_s, 1),
        "requetes_par_s": round(len(prompts) / duree_s, 2),
        "tokens_generes": nb_tokens,
        "tokens_par_s": round(nb_tokens / duree_s),
    }
    return resume, textes


def main(moteur, nb_cas, taille_lot, seed):
    prompts = [construire_prompt("triage", cas) for cas in lire_cas(nb_cas, seed)]

    debut = time.perf_counter()
    generer, tokenizer = moteur_vllm() if moteur == "vllm" else moteur_transformers(taille_lot)
    chargement_s = time.perf_counter() - debut
    print(f"{moteur} : chargement {chargement_s:.0f} s")

    # Premier appel hors mesure : initialisation CUDA et compilation.
    generer(prompts[:1])

    resultats = {"moteur": moteur, "nb_cas": nb_cas, "seed": seed, "chargement_s": round(chargement_s)}
    if moteur == "transformers":
        resultats["taille_lot"] = taille_lot
    for mode, un_par_un in [("un_par_un", True), ("tous_ensemble", False)]:
        resume, textes = mesurer(generer, tokenizer, prompts, un_par_un)
        resultats[mode] = {"resume": resume, "textes": textes}
        print(f"{moteur}, {mode} : {resume}")

    DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)
    chemin = DOSSIER_SORTIE / f"moteur_{moteur}_{time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(resultats, f, ensure_ascii=False, indent=2)
    print(f"résultats : {chemin}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--moteur", choices=["vllm", "transformers"], required=True)
    parser.add_argument("--nb-cas", type=int, default=48)
    parser.add_argument("--taille-lot", type=int, default=8, help="transformers seulement")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    main(args.moteur, args.nb_cas, args.taille_lot, args.seed)
