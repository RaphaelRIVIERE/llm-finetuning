"""Compare plusieurs réglages de SamplingParams vLLM, sur les exemples de evaluate_dpo.py
ou sur des questions libres écrites à la main."""

import argparse
from pathlib import Path

from datasets import load_dataset
from vllm import LLM, SamplingParams

CHEMIN_MODELE = "runs/final"
DOSSIER_DATASET = Path("data/export/sft")
N_FRANCAIS = 5
N_ANGLAIS = 5

# Passage 1 : configuration A (celle de l'API au départ) contre des alternatives qui
# remplacent ou complètent repetition_penalty, faute d'équivalent à no_repeat_ngram_size
# dans vLLM.
# Passage 2 : affinage de frequency_penalty, meilleure piste du passage 1, avec plus de
# tokens pour ne plus couper les réponses longues.
PASSAGES = {
    1: dict(
        rapport=Path("docs/test_decodage_vllm.md"),
        max_tokens=256,
        configurations={
            "A_actuelle": dict(repetition_penalty=1.3),
            "B_penalite_1.1": dict(repetition_penalty=1.1),
            "C_sans_penalite": dict(repetition_penalty=1.0),
            "D_frequence": dict(repetition_penalty=1.0, frequency_penalty=0.5),
            "E_mixte": dict(repetition_penalty=1.1, presence_penalty=0.3),
        },
    ),
    2: dict(
        rapport=Path("docs/test_decodage_vllm_2.md"),
        max_tokens=512,
        configurations={
            "frequence_0.3": dict(frequency_penalty=0.3),
            "frequence_0.5": dict(frequency_penalty=0.5),
            "frequence_0.7": dict(frequency_penalty=0.7),
        },
    ),
    # Passage 3 : questions libres, hors du format « Cas clinique / Question » de
    # l'entraînement. Chaque cas est posé deux fois, à la première personne comme un
    # patient, puis à la troisième personne comme un cas clinique, pour mesurer la
    # sensibilité à la formulation. Pas de réponse attendue : on juge la forme (boucle,
    # mots inventés, langue, cohérence entre formulations), pas la justesse médicale,
    # qui demande une référence validée par un clinicien.
    3: dict(
        rapport=Path("docs/test_decodage_vllm_3.md"),
        max_tokens=512,
        configurations={
            "frequence_0.5": dict(frequency_penalty=0.5),
            "frequence_0.5_repetition_1.1": dict(frequency_penalty=0.5, repetition_penalty=1.1),
            "frequence_0.5_presence_0.5": dict(frequency_penalty=0.5, presence_penalty=0.5),
        },
        questions=[
            dict(
                langue="fr",
                instruction="J'ai 35 ans avec des douleur en bas du dos, douleur a l'épaule et au genoux. Quel diagnostic peut être envisagé au vu des signes cliniques et biologiques ?",
            ),
            dict(
                langue="fr",
                instruction="Homme de 35 ans avec des douleur en bas du dos, douleur a l'épaule et au genoux. Quel diagnostic peut être envisagé au vu des signes cliniques et biologiques ?",
            ),
            dict(
                langue="fr",
                instruction="J'ai 58 ans, je fume, et j'ai une douleur dans la poitrine qui serre et qui descend dans le bras gauche depuis 30 minutes. Qu'est-ce que j'ai ?",
            ),
            dict(
                langue="fr",
                instruction="Homme de 58 ans, fumeur, douleur thoracique constrictive irradiant dans le bras gauche depuis 30 minutes. Quel diagnostic évoquer ?",
            ),
            dict(
                langue="fr",
                instruction="J'ai 45 ans et d'un coup j'ai eu un mal de tête très violent, le pire de ma vie, avec envie de vomir. Qu'est-ce que ça peut être ?",
            ),
            dict(
                langue="fr",
                instruction="Femme de 45 ans, céphalée brutale en coup de tonnerre, d'intensité maximale d'emblée, avec nausées. Quel diagnostic évoquer ?",
            ),
            dict(
                langue="fr",
                instruction="J'ai 25 ans, j'ai le nez qui coule, mal à la gorge et un peu de fièvre depuis 2 jours. Qu'est-ce que j'ai ?",
            ),
            dict(
                langue="fr",
                instruction="Homme de 25 ans, rhinorrhée, odynophagie et fébricule depuis 2 jours. Quel diagnostic évoquer ?",
            ),
            dict(
                langue="en",
                instruction="I'm 30 and I have a fever, a stiff neck and a bad headache, and light hurts my eyes. What do I have?",
            ),
            dict(
                langue="en",
                instruction="A 30-year-old woman presents with fever, neck stiffness, headache and photophobia. What diagnosis should be considered?",
            ),
        ],
    ),
}


def selectionner_exemples(dataset, langue, n):
    sous_ensemble = dataset.filter(lambda ex: ex["langue"] == langue)
    return sous_ensemble.select(range(min(n, len(sous_ensemble))))


def ecrire_rapport_md(exemples, resultats, passage):
    config = PASSAGES[passage]
    lignes = [
        f"# Test des paramètres de décodage vLLM, passage {passage}",
        "",
        f"Modèle : `{CHEMIN_MODELE}`. Greedy (temperature=0), max_tokens={config['max_tokens']}.",
        "Référence Transformers : colonne « Après DPO » de `docs/evaluation_dpo.md`."
        if "questions" not in config
        else "Questions libres écrites à la main, sans réponse attendue : on juge la forme, pas la justesse médicale.",
        "",
        "## Configurations",
        "",
    ]
    for nom, params in config["configurations"].items():
        lignes.append(f"- `{nom}` : {params}")
    lignes.append("")

    for i, exemple in enumerate(exemples):
        lignes += [
            f"## Exemple {i + 1} ({exemple['langue']})",
            "",
            "**Instruction**",
            "",
            exemple["instruction"],
            "",
        ]
        if "reponse" in exemple:
            lignes += ["**Réponse attendue**", "", exemple["reponse"], ""]
        for nom, sorties in resultats.items():
            sortie = sorties[i].outputs[0]
            lignes += [
                f"**{nom}** ({len(sortie.token_ids)} tokens, arrêt : {sortie.finish_reason})",
                "",
                sortie.text,
                "",
            ]
    chemin = config["rapport"]
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text("\n".join(lignes), encoding="utf-8")
    print(f"Rapport écrit dans {chemin}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--passage", type=int, choices=sorted(PASSAGES), default=3)
    args = parser.parse_args()
    config = PASSAGES[args.passage]

    if "questions" in config:
        exemples = config["questions"]
    else:
        eval_clinique = load_dataset("json", data_files=str(DOSSIER_DATASET / "eval_clinique.jsonl"), split="train")
        exemples_fr = selectionner_exemples(eval_clinique, "fr", N_FRANCAIS)
        exemples_en = selectionner_exemples(eval_clinique, "en", N_ANGLAIS)
        exemples = list(exemples_fr) + list(exemples_en)
    instructions = [ex["instruction"] for ex in exemples]

    # Mêmes réglages mémoire que l'API (app/main.py).
    print("Chargement du modèle dans vLLM (peut prendre quelques minutes)...", flush=True)
    llm = LLM(model=CHEMIN_MODELE, dtype="bfloat16", gpu_memory_utilization=0.8, max_model_len=4096)

    resultats = {}
    for nom, params in config["configurations"].items():
        print(f"Génération avec {nom}...", flush=True)
        sampling = SamplingParams(max_tokens=config["max_tokens"], temperature=0.0, **params)
        resultats[nom] = llm.generate(instructions, sampling)

    ecrire_rapport_md(exemples, resultats, args.passage)
