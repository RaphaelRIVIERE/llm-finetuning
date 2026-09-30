"""Fonctions de chargement et conversion des sources vers le schéma commun."""

import random
from collections import defaultdict

from datasets import load_dataset
from sklearn.model_selection import train_test_split

from scripts.anonymisation import anonymize_french_sources, anonymize_text
from scripts.cases import case_key, dedupe_cases, is_triage_case, normalize_text, remove_choices
from scripts.patient_names import find_leftover_names

RATIOS_SPLITS = {"train": 0.8, "validation": 0.1, "test": 0.05, "eval_clinique": 0.05}
TAILLE_CIBLE_SFT = 5000

# Commits Hugging Face des sources, fixés pour que le dataset produit ne change pas si un
# auteur met à jour sa source. Ce sont les versions utilisées pour l'exploration.
REVISIONS = {
    "ANR-MALADES/MediQAl": "5af34948a74c7b8807c476204a21149ffb00ea2c",
    "nthngdy/frenchmedmcqa": "6195120803580d171cbf2172c0beac03f21d14fb",
    "keivalya/MedQuad-MedicalQnADataset": "5b0961fbaa6d7f9c344c5d59c29943fb900c2eca",
    "TsinghuaC3I/UltraMedical-Preference": "761eb7935310ba662a96d93c5af342e5269d5759",
}


def load_mediqa():
    """Charge MediQAl (config oeq), sans split."""
    dataset = load_dataset("ANR-MALADES/MediQAl", "oeq", revision=REVISIONS["ANR-MALADES/MediQAl"])
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


# Les configs QCM ont aussi des cas cliniques, qui servent au triage. Le QA en texte
# libre reste sur oeq (load_mediqa).
CONFIGS_MEDIQAL = ["oeq", "mcqm", "mcqu"]


def load_mediqal_cases():
    """Cas cliniques uniques et anonymisés de MediQAl, pour le triage."""
    cas_uniques = {}
    for config in CONFIGS_MEDIQAL:
        dataset = load_dataset("ANR-MALADES/MediQAl", config, revision=REVISIONS["ANR-MALADES/MediQAl"])
        for split in dataset.values():
            for cas in split["clinical_case"]:
                if cas:
                    cas_uniques.setdefault(normalize_text(cas), cas.strip())

    records = []
    for cas in sorted(cas_uniques.values()):
        anonymise = anonymize_text(cas)
        if anonymise is None:
            continue
        texte, touche = anonymise
        records.append({
            "id": f"mediqal_cas_{len(records)}",
            "langue": "fr",
            "source": "mediqal",
            "licence_source": "CC-BY-4.0",
            "niveau_confiance": "haut",
            "transformations": ["anonymisation_noms"] if touche else [],
            "cas": texte,
            "cle_cas": case_key(texte),
        })
    return records


LETTRES_FRENCHMEDMCQA = ["a", "b", "c", "d", "e"]


def load_frenchmedmcqa():
    """Charge FrenchMedMCQA et reformule le QCM en question/réponse."""
    dataset = load_dataset("nthngdy/frenchmedmcqa", revision=REVISIONS["nthngdy/frenchmedmcqa"])
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
                "licence_source": "Apache 2.0",
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
    """Charge MedQuAD, sans split."""
    dataset = load_dataset("keivalya/MedQuad-MedicalQnADataset", revision=REVISIONS["keivalya/MedQuad-MedicalQnADataset"])
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
                "niveau_confiance": "moyen",
                "transformations": [],
                "instruction": ex["Question"].strip(),
                "reponse": ex["Answer"].strip(),
                "symptomes": [],
                "antecedents": [],
                "constantes_vitales": {},
            })
            compteur += 1
    return records


# Questions de forum écrites par de vrais patients, avec parfois leur nom, leur ville ou
# leur numéro (notebook 02). Écartées plutôt qu'anonymisées : aucun motif ne garantit de
# tout retirer, et le DPO garde largement assez de paires sans elles.
ORIGINES_ULTRAMEDICAL_ECARTEES = {"ChatDoctor", "Medical-Instruct-120k"}


def load_ultramedical_preference():
    """Charge UltraMedical-Preference sans les fuites train/validation, les questions de
    forum et les paires où un nom est repéré."""
    dataset = load_dataset("TsinghuaC3I/UltraMedical-Preference", revision=REVISIONS["TsinghuaC3I/UltraMedical-Preference"])
    fuite = set(dataset["train"]["prompt_id"]) & set(dataset["validation"]["prompt_id"])
    records = []
    compteur = 0
    for split_name, split in dataset.items():
        for ex in split:
            if split_name == "train" and ex["prompt_id"] in fuite:
                continue
            if ex["prompt_id"].split(",")[0] in ORIGINES_ULTRAMEDICAL_ECARTEES:
                continue
            prompt = ex["prompt"].strip()
            chosen = ex["chosen"][-1]["content"].strip()
            rejected = ex["rejected"][-1]["content"].strip()
            if any(find_leftover_names(texte, "en") for texte in (prompt, chosen, rejected)):
                continue
            records.append({
                "id": f"ultramedical_preference_{compteur}",
                "langue": "en",
                "source": "ultramedical_preference",
                "licence_source": "MIT",
                "split": split_name,
                "niveau_confiance": "moyen",
                "transformations": [],
                "prompt": prompt,
                "chosen": chosen,
                "rejected": rejected,
            })
            compteur += 1
    return records


def load_ultramedical_cases():
    """Prompts uniques d'UltraMedical-Preference, pour le triage, sans les choix du QCM.
    Mêmes exclusions que load_ultramedical_preference : forums écartés, prompts où un nom
    est repéré. Les prompts sans choix au format « A. » sont écartés aussi."""
    dataset = load_dataset("TsinghuaC3I/UltraMedical-Preference", revision=REVISIONS["TsinghuaC3I/UltraMedical-Preference"])
    prompts_uniques = {}
    for split in dataset.values():
        for prompt, prompt_id in zip(split["prompt"], split["prompt_id"]):
            if prompt_id.split(",")[0] in ORIGINES_ULTRAMEDICAL_ECARTEES:
                continue
            prompts_uniques.setdefault(normalize_text(prompt), prompt.strip())

    records = []
    for prompt in sorted(prompts_uniques.values()):
        if find_leftover_names(prompt, "en"):
            continue
        cas = remove_choices(prompt)
        if cas is None:
            continue
        records.append({
            "id": f"ultramedical_cas_{len(records)}",
            "langue": "en",
            "source": "ultramedical_preference",
            "licence_source": "MIT",
            "niveau_confiance": "moyen",
            "transformations": ["retrait_choix_qcm"],
            "cas": cas,
            "cle_cas": case_key(cas),
        })
    return records


def load_triage_cases():
    """Cas à annoter : les cas de triage de MediQAl et d'UltraMedical, un seul par clé de
    cas. Entre les deux sources, le texte ne peut pas trouver de doublon (français contre
    anglais), le dédoublonnage se fait donc dans chaque source."""
    records = []
    for record in load_mediqal_cases() + load_ultramedical_cases():
        if is_triage_case(record["cas"], record["langue"]):
            records.append(record)
    return dedupe_cases(records)


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
    """Retire les doublons exacts (prompt, chosen, rejected), garde la première occurrence."""
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
    """Répartit les records selon RATIOS_SPLITS, stratifié par source."""
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
    """Agrège les sources SFT, dédoublonne, anonymise puis répartit en splits."""
    records = []
    records += load_mediqa()
    records += load_frenchmedmcqa()
    records += load_medquad()
    records = clean_sft_dataset(records)
    records = anonymize_french_sources(records)
    return assign_splits(records)


def subsample_sft_dataset(records, taille_cible=TAILLE_CIBLE_SFT, seed=42):
    """Tire environ `taille_cible` paires en gardant les proportions de chaque
    (source, split)."""
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
    """Charge UltraMedical-Preference puis dédoublonne les triples exacts."""
    records = load_ultramedical_preference()
    return clean_dpo_dataset(records)
