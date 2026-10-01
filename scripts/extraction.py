"""Fonctions de chargement et conversion des sources vers le schéma commun."""

import json
from pathlib import Path

from datasets import load_dataset
from tqdm import tqdm

from scripts.anonymisation import anonymize_french_sources, anonymize_text
from scripts.cases import (
    case_key, dedupe_cases, drop_short_vignettes, is_triage_case, normalize_text, remove_choices,
    remove_double_question_mark, split_cases,
)
from scripts.examples import (
    apply_translations, build_dpo_examples, build_qa_examples, build_triage_examples, keep_scored_preferences, sample_qa_examples,
)
from scripts.patient_names import find_leftover_names

# Nombre d'exemples de QA ajoutés aux exemples de triage
TAILLE_QA = 1000
FICHIER_ANNOTATIONS = Path(__file__).resolve().parent.parent / "data" / "annotation" / "annotations.jsonl"
FICHIER_TRADUCTIONS = FICHIER_ANNOTATIONS.parent / "traductions_en.jsonl"

# Commits Hugging Face des sources, fixés pour que le dataset produit ne change pas si un
# auteur met à jour sa source. Ce sont les versions utilisées pour l'exploration.
REVISIONS = {
    "ANR-MALADES/MediQAl": "5af34948a74c7b8807c476204a21149ffb00ea2c",
    "nthngdy/frenchmedmcqa": "6195120803580d171cbf2172c0beac03f21d14fb",
    "keivalya/MedQuad-MedicalQnADataset": "5b0961fbaa6d7f9c344c5d59c29943fb900c2eca",
    "TsinghuaC3I/UltraMedical-Preference": "761eb7935310ba662a96d93c5af342e5269d5759",
}


def anonymized_case_key(text):
    """Clé de cas calculée sur le texte anonymisé, comme pour les cas de triage."""
    anonymise = anonymize_text(text.strip())
    return case_key(anonymise[0] if anonymise else text)


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
                # le cas clinique s'il y en a un, sinon la question
                "cle_cas": anonymized_case_key(ex["clinical_case"] or question),
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
                # la question seule, sans les propositions
                "cle_cas": anonymized_case_key(ex["question"]),
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
            question = ex["Question"].strip()
            instruction = remove_double_question_mark(question)
            records.append({
                "id": f"medquad_{compteur}",
                "langue": "en",
                "source": "medquad",
                "licence_source": "CC-BY-4.0",
                "split": None,
                "niveau_confiance": "moyen",
                "transformations": ["correction_ponctuation"] if instruction != question else [],
                "instruction": instruction,
                "reponse": ex["Answer"].strip(),
                # sur la question d'origine, pour ne pas changer le découpage
                "cle_cas": case_key(question),
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
    """Charge UltraMedical-Preference sans les questions de forum ni les paires où un nom
    est repéré. Le split de la source est gardé pour mémoire : le découpage par cas le
    remplace, ce qui règle aussi les prompts présents à la fois en train et en validation."""
    dataset = load_dataset("TsinghuaC3I/UltraMedical-Preference", revision=REVISIONS["TsinghuaC3I/UltraMedical-Preference"])
    records = []
    compteur = 0
    for split_name, split in dataset.items():
        for ex in tqdm(split, desc=f"UltraMedical-Preference {split_name}"):
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
                "cle_cas": case_key(prompt),
                # comment la source a construit la paire (hard, length, easy, human) et
                # la note sur 5 de chaque réponse
                "type_paire": ex["label_type"],
                "score_chosen": ex["metadata"]["chosen"]["score"],
                "score_rejected": ex["metadata"]["rejected"]["score"],
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


def load_annotations(path=FICHIER_ANNOTATIONS, path_traductions=FICHIER_TRADUCTIONS):
    """Cas de triage annotés par scripts/annotation.py, avec leur `urgency_level`. Un
    cas dont la réponse est invalide est gardé, sans niveau. Les vignettes anglaises trop
    courtes sont écartées (`drop_short_vignettes`). Les champs texte des cas anglais sont
    remplacés par leur traduction (scripts/traduction.py) quand elle existe."""
    with open(path, encoding="utf-8") as f:
        annotations = drop_short_vignettes([json.loads(ligne) for ligne in f])
    traductions = []
    if path_traductions.exists():
        with open(path_traductions, encoding="utf-8") as f:
            traductions = [json.loads(ligne) for ligne in f]
    annotations = apply_translations(annotations, traductions)
    for record in annotations:
        record["urgency_level"] = record["sortie"]["urgency_level"] if record["valide"] else None
    return annotations


def load_split_units():
    """Tout ce qui entre dans le découpage : cas de triage annotés, QA de MediQAl,
    FrenchMedMCQA et MedQuAD, prompts UltraMedical. Chaque record a une `cle_cas`."""
    return (
        load_annotations() + load_mediqa() + load_frenchmedmcqa() + load_medquad()
        + load_ultramedical_preference()
    )


def build_case_splits(seed=42):
    """Découpage global par cas, toutes sources ensemble. Renvoie {cle_cas: split}."""
    return split_cases(load_split_units(), seed)


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


def build_sft_dataset(n_qa=TAILLE_QA, seed=42):
    """Dataset SFT : tous les exemples de triage, plus `n_qa` exemples de QA. Les splits
    viennent du découpage global par cas."""
    records = load_split_units()
    splits = split_cases(records, seed)
    # un cas annoté a un champ `cas`, une question de QA un champ `instruction`
    triage = build_triage_examples([r for r in records if "cas" in r], splits)
    qa = clean_sft_dataset([r for r in records if "instruction" in r])
    qa = build_qa_examples(anonymize_french_sources(qa), splits)
    return triage + sample_qa_examples(qa, n_qa, seed)


def build_dpo_dataset(seed=42):
    """Dataset DPO : les paires UltraMedical-Preference sans les triples en double ni les
    paires où la réponse préférée n'a pas le meilleur score. Les splits viennent du
    découpage global par cas, le même que pour le SFT."""
    records = load_split_units()
    splits = split_cases(records, seed)
    # une paire de préférences a un champ `prompt`
    paires = clean_dpo_dataset([r for r in records if "prompt" in r])
    return build_dpo_examples(keep_scored_preferences(paires), splits)
