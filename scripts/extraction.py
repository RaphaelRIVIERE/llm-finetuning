"""Fonctions de chargement et conversion des sources vers le schéma commun."""

import random
from collections import defaultdict

from datasets import load_dataset
from sklearn.model_selection import train_test_split

RATIOS_SPLITS = {"train": 0.8, "validation": 0.1, "test": 0.05, "eval_clinique": 0.05}
TAILLE_CIBLE_SFT = 5000


def load_mediqa():
    """Charge MediQAl (config oeq). Split laissé à None, assigné plus tard sur l'agrégat."""
    dataset = load_dataset("ANR-MALADES/MediQAl", "oeq")
    records = []
    for split in dataset.values():
        for ex in split:
            question = ex["question"].strip()
            if ex["clinical_case"] is not None:
                instruction = f"Cas clinique : {ex['clinical_case'].strip()}\n\nQuestion : {question}"
            else:
                instruction = question
            records.append({
                "id": f"mediqal_{ex['id']}",
                "langue": "fr",
                "source": "mediqal",
                "licence_source": "CC-BY-4.0",
                "split": None,
                "niveau_confiance": "haut",
                "transformations": [],
                "instruction": instruction,
                "reponse": ex["answer"].strip(),
                "symptomes": [],
                "antecedents": [],
                "constantes_vitales": {},
            })
    return records


LETTRES_FRENCHMEDMCQA = ["a", "b", "c", "d", "e"]


def load_frenchmedmcqa():
    """Charge FrenchMedMCQA et reformule le QCM en question/réponse. `correct_answers`
    est l'index (0 à 4) de la bonne proposition, pas un ClassLabel."""
    dataset = load_dataset("nthngdy/frenchmedmcqa")
    records = []
    for split_name, split in dataset.items():
        for ex in split:
            propositions = [ex[f"answer_{lettre}"] for lettre in LETTRES_FRENCHMEDMCQA]
            instruction = ex["question"].strip() + "\n" + "\n".join(
                f"{lettre}) {proposition}" for lettre, proposition in zip(LETTRES_FRENCHMEDMCQA, propositions)
            )
            correct_index = ex["correct_answers"]
            reponse = f"{LETTRES_FRENCHMEDMCQA[correct_index]}) {propositions[correct_index]}"
            records.append({
                "id": f"frenchmedmcqa_{ex['id']}",
                "langue": "fr",
                "source": "frenchmedmcqa",
                "licence_source": "non spécifiée",
                "split": split_name,
                "niveau_confiance": "haut",
                "transformations": ["reformulation_qcm_vers_qa"],
                "instruction": instruction,
                "reponse": reponse,
                "symptomes": [],
                "antecedents": [],
                "constantes_vitales": {},
            })
    return records


def load_medquad():
    """Charge MedQuAD. Split laissé à None, dédoublonnage fait plus tard sur l'agrégat."""
    dataset = load_dataset("keivalya/MedQuad-MedicalQnADataset")
    records = []
    compteur = 0
    for split in dataset.values():
        for ex in split:
            records.append({
                "id": f"medquad_{compteur}",
                "langue": "en",
                "source": "medquad",
                "licence_source": "CC-BY-4.0",
                "split": None,
                "niveau_confiance": "haut",
                "transformations": [],
                "instruction": ex["Question"].strip(),
                "reponse": ex["Answer"].strip(),
                "symptomes": [],
                "antecedents": [],
                "constantes_vitales": {},
            })
            compteur += 1
    return records


def load_ultramedical_preference():
    """Charge UltraMedical-Preference. Retire du train les prompt_id qui fuitent vers
    validation. chosen/rejected : conversations à 2 tours, on garde la réponse finale."""
    dataset = load_dataset("TsinghuaC3I/UltraMedical-Preference")
    fuite = set(dataset["train"]["prompt_id"]) & set(dataset["validation"]["prompt_id"])
    records = []
    compteur = 0
    for split_name, split in dataset.items():
        for ex in split:
            if split_name == "train" and ex["prompt_id"] in fuite:
                continue
            records.append({
                "id": f"ultramedical_preference_{compteur}",
                "langue": "en",
                "source": "ultramedical_preference",
                "licence_source": "MIT",
                "split": split_name,
                "niveau_confiance": "moyen",
                "transformations": [],
                "prompt": ex["prompt"].strip(),
                "chosen": ex["chosen"][-1]["content"].strip(),
                "rejected": ex["rejected"][-1]["content"].strip(),
            })
            compteur += 1
    return records


def clean_sft_dataset(records):
    """Retire les doublons exacts (instruction, reponse), garde la première occurrence."""
    vus = set()
    nettoyes = []
    for record in records:
        cle = (record["instruction"], record["reponse"])
        if cle in vus:
            continue
        vus.add(cle)
        nettoyes.append(record)
    return nettoyes


def clean_dpo_dataset(records):
    """Retire les doublons exacts (prompt, chosen, rejected), garde la première occurrence.
    Vérifié séparément que ces doublons ne traversent jamais deux splits différents."""
    vus = set()
    nettoyes = []
    for record in records:
        cle = (record["prompt"], record["chosen"], record["rejected"])
        if cle in vus:
            continue
        vus.add(cle)
        nettoyes.append(record)
    return nettoyes


def assign_splits(records, seed=42):
    """Répartit les records selon RATIOS_SPLITS, stratifié par source. Écrase le
    split déjà présent sur certaines sources (FrenchMedMCQA)."""
    sources = [record["source"] for record in records]
    train, reste = train_test_split(
        records, test_size=1 - RATIOS_SPLITS["train"], stratify=sources, random_state=seed
    )

    part_validation = RATIOS_SPLITS["validation"] / (1 - RATIOS_SPLITS["train"])
    sources_reste = [record["source"] for record in reste]
    validation, reste = train_test_split(
        reste, test_size=1 - part_validation, stratify=sources_reste, random_state=seed
    )

    sources_reste = [record["source"] for record in reste]
    test, eval_clinique = train_test_split(
        reste, test_size=0.5, stratify=sources_reste, random_state=seed
    )

    for nouveau_split, split_records in [
        ("train", train), ("validation", validation), ("test", test), ("eval_clinique", eval_clinique)
    ]:
        for record in split_records:
            if record["split"] is not None and record["split"] != nouveau_split:
                record["transformations"].append("split_reassigne")
            record["split"] = nouveau_split
    return records


def build_sft_dataset():
    """Agrège MediQA, FrenchMedMCQA et MedQuAD au format commun, dédoublonne,
    puis répartit en train/validation/test/eval_clinique."""
    records = []
    records += load_mediqa()
    records += load_frenchmedmcqa()
    records += load_medquad()
    records = clean_sft_dataset(records)
    return assign_splits(records)


def subsample_sft_dataset(records, taille_cible=TAILLE_CIBLE_SFT, seed=42):
    """Sous-échantillonne l'agrégat SFT à environ `taille_cible` paires, en tirant
    une fraction proportionnelle dans chaque (source, split). Choix documenté dans
    `docs/decisions.md`."""
    rng = random.Random(seed)
    fraction = taille_cible / len(records)

    par_stratum = defaultdict(list)
    for record in records:
        par_stratum[(record["source"], record["split"])].append(record)

    echantillon = []
    for stratum_records in par_stratum.values():
        # suppose taille_cible << len(records) : sinon n peut dépasser la taille
        # de la strate et rng.sample lève une erreur
        n = round(len(stratum_records) * fraction)
        echantillon += rng.sample(stratum_records, n)
    return echantillon


def build_sft_sample():
    """Agrégat SFT complet, sous-échantillonné."""
    return subsample_sft_dataset(build_sft_dataset())


def build_dpo_dataset():
    """Construit le dataset DPO : charge UltraMedical-Preference (fuite déjà
    retirée) puis dédoublonne les triples exacts."""
    records = load_ultramedical_preference()
    return clean_dpo_dataset(records)
