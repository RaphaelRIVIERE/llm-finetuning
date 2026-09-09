"""Sauvegarde d'échantillons de datasets pour inspection manuelle."""

import json
from pathlib import Path

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "data" / "samples"


def save_sample(dataset_dict, name, n_samples=20, samples_dir=SAMPLES_DIR):
    """Écrit un échantillon de chaque split d'un DatasetDict en JSON lisible."""
    for split, dataset in dataset_dict.items():
        n = min(n_samples, len(dataset))
        sample = [dataset[i] for i in range(n)]
        path = Path(samples_dir) / name / f"{split}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(sample, f, ensure_ascii=False, indent=2)
        print(f"{name}/{split} : {n} exemples écrits dans {path}")
