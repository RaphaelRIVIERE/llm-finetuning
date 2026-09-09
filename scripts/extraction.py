"""Fonctions de chargement et conversion des sources vers le schéma commun."""

from datasets import load_dataset


def load_mediqa():
    """Charge MediQA et retourne une liste de dicts au schéma commun."""
    dataset = load_dataset("ANR-MALADES/MediQAl")
    raise NotImplementedError("Mapping des champs à écrire après exploration")


def load_frenchmedmcqa():
    """Charge FrenchMedMCQA et retourne une liste de dicts au schéma commun."""
    dataset = load_dataset("nthngdy/frenchmedmcqa")
    raise NotImplementedError("Mapping des champs à écrire après exploration")


def load_medquad():
    """Charge MedQuAD et retourne une liste de dicts au schéma commun."""
    dataset = load_dataset("keivalya/MedQuad-MedicalQnADataset")
    raise NotImplementedError("Mapping des champs à écrire après exploration")


def load_ultramedical_preference():
    """Charge UltraMedical-Preference pour construire le dataset DPO."""
    dataset = load_dataset("TsinghuaC3I/UltraMedical-Preference")
    raise NotImplementedError("Mapping des champs à écrire après exploration")


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
