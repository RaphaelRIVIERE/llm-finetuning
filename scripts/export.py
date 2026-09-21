"""Export des datasets SFT et DPO finaux en JSONL, un fichier par split."""

import json
from pathlib import Path

from scripts.extraction import build_dpo_dataset, build_sft_sample

DOSSIER_EXPORT = Path("data/export")


def write_jsonl(records, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def export_by_split(records, output_dir):
    """Regroupe les records par split et écrit un fichier JSONL par split.
    Renvoie le nombre d'exemples écrits par split, pour vérification."""
    par_split = {}
    for record in records:
        par_split.setdefault(record["split"], []).append(record)
    for split, split_records in par_split.items():
        write_jsonl(split_records, output_dir / f"{split}.jsonl")
    return {split: len(split_records) for split, split_records in par_split.items()}


def export_datasets(output_dir=DOSSIER_EXPORT):
    sft = build_sft_sample()
    dpo = build_dpo_dataset()
    return {
        "sft": export_by_split(sft, output_dir / "sft"),
        "dpo": export_by_split(dpo, output_dir / "dpo"),
    }


if __name__ == "__main__":
    counts = export_datasets()
    for config, par_split in counts.items():
        total = sum(par_split.values())
        print(f"{config} : {total} exemples")
        for split, n in sorted(par_split.items()):
            print(f"  {split:15s} {n:6d}")
