"""Sauvegarde d'échantillons de datasets pour inspection manuelle."""

import json
import random
from pathlib import Path

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "data" / "samples"


def first_split(dataset_dict):
    """Renvoie le nom et le contenu du premier split d'un DatasetDict."""
    name = list(dataset_dict.keys())[0]
    return name, dataset_dict[name]


def save_sample(dataset_dict, name, n_samples=20, samples_dir=SAMPLES_DIR, seed=42):
    """Écrit un échantillon de chaque split d'un DatasetDict en JSON lisible. Les lignes
    sont tirées au hasard avec une graine fixe : les premières lignes d'un dataset viennent
    souvent de quelques cas seulement (jusqu'à 12 questions par cas dans MediQAl)."""
    rng = random.Random(seed)
    for split, dataset in dataset_dict.items():
        n = min(n_samples, len(dataset))
        indices = sorted(rng.sample(range(len(dataset)), n))
        sample = [dataset[i] for i in indices]
        path = Path(samples_dir) / name / f"{split}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(sample, f, ensure_ascii=False, indent=2)
        print(f"{name}/{split} : {n} exemples tirés au hasard écrits dans {path}")
