"""Fonctions de chargement et conversion des sources vers le schéma commun."""

from datasets import load_dataset


def load_mediqa():
    """Charge MediQAl (config oeq). Split laissé à None : la séparation
    train/validation/test/eval_clinique se fera plus tard sur l'agrégat."""
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
    """Charge FrenchMedMCQA et reformule le QCM en question/réponse.
    `correct_answers` est déjà l'index (0 à 4) de la bonne proposition, pas un ClassLabel."""
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
    """Charge MedQuAD. Split laissé à None comme pour MediQAl. Les 48 doublons
    exacts ne sont pas retirés ici, le dédoublonnage se fera sur l'agrégat."""
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
    """Charge UltraMedical-Preference. Retire du train les prompt_id aussi présents
    en validation (raison dans docs/decisions.md). chosen/rejected sont des
    conversations à 2 tours, on ne garde que la réponse (dernier tour)."""
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


def build_sft_dataset():
    """Agrège les sources SFT (MediQA, FrenchMedMCQA, MedQuAD) au format commun."""
    records = []
    records += load_mediqa()
    records += load_frenchmedmcqa()
    records += load_medquad()
    return records


def build_dpo_dataset():
    """Construit le dataset DPO à partir des paires préférentielles."""
    return load_ultramedical_preference()
