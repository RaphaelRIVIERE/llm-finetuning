"""Construction des exemples SFT à partir des cas et du découpage par cas. Pas de
dépendance lourde, pour que les tests tournent dans la CI."""

import random
from collections import Counter, defaultdict

from app.triage import SortieTriage, vers_json


def apply_translations(annotations, traductions):
    """Remplace les champs texte de la sortie (justification, recommandation, symptômes,
    signes d'alerte) par leur traduction anglaise, pour les cas qui en ont une valide. Le
    niveau et la spécialité ne sont pas touchés."""
    par_id = {t["id"]: t["traduction"] for t in traductions if t["valide"]}
    traduites = []
    for annotation in annotations:
        traduction = par_id.get(annotation["id"])
        if traduction:
            annotation = {
                **annotation,
                "sortie": {**annotation["sortie"], **traduction},
                "transformations": annotation["transformations"] + ["traduction_anglais"],
            }
        traduites.append(annotation)
    return traduites


def build_triage_examples(annotations, splits):
    """Exemples de triage : le cas en instruction, la sortie de triage en JSON en réponse.
    `splits` est le découpage par cas ({cle_cas: split}). Les annotations invalides sont
    écartées. La consigne n'est pas dans l'exemple, elle est ajoutée au moment de
    construire le prompt."""
    examples = []
    for annotation in annotations:
        if not annotation["valide"]:
            continue
        # repasser par le modèle Pydantic garantit l'ordre des clés du JSON
        sortie = SortieTriage.model_validate(annotation["sortie"])
        examples.append({
            "id": annotation["id"],
            "langue": annotation["langue"],
            "source": annotation["source"],
            "licence_source": annotation["licence_source"],
            "split": splits[annotation["cle_cas"]],
            "niveau_confiance": annotation["niveau_confiance"],
            "transformations": annotation["transformations"] + ["annotation_triage"],
            "tache": "triage",
            "instruction": annotation["cas"],
            "reponse": vers_json(sortie),
            "cle_cas": annotation["cle_cas"],
            "urgency_level": sortie.urgency_level.value,
            "symptomes": sortie.key_symptoms,
            "antecedents": annotation["antecedents"],
            "constantes_vitales": annotation["constantes_vitales"],
            "annotateur": annotation["annotateur"],
            "version_prompt": annotation["version_prompt"],
        })
    return examples


def with_case_split(record, splits):
    """Copie du record avec le split de sa clé de cas, qui remplace celui de la source."""
    split = splits[record["cle_cas"]]
    transformations = list(record["transformations"])
    if record["split"] is not None and record["split"] != split:
        transformations.append("split_reassigne")
    return {**record, "split": split, "transformations": transformations}


def build_qa_examples(records, splits):
    """Exemples de QA : la question en instruction, la réponse en texte libre. Le split
    vient du découpage par cas."""
    examples = []
    for record in records:
        examples.append({
            **with_case_split(record, splits),
            "tache": "qa",
            # champs du triage, vides ici pour garder les mêmes colonnes
            "urgency_level": None,
            "annotateur": None,
            "version_prompt": None,
        })
    return examples


def keep_scored_preferences(records):
    """Garde les paires où la réponse préférée a un score strictement meilleur que la
    réponse écartée. Dans les autres, la préférence ne repose sur rien de mesuré."""
    return [record for record in records if record["score_chosen"] > record["score_rejected"]]


def sample_balanced_by_length(paires, n, seed=42):
    """Tire `n` paires DPO, moitié où la réponse préférée est la plus longue, moitié où
    elle est la plus courte (ou de même longueur). Le DPO ne peut plus apprendre que plus
    long veut dire meilleur."""
    rng = random.Random(seed)
    plus_longues = [p for p in paires if len(p["chosen"]) > len(p["rejected"])]
    autres = [p for p in paires if len(p["chosen"]) <= len(p["rejected"])]
    moitie = n // 2
    tirage = rng.sample(plus_longues, min(moitie, len(plus_longues)))
    tirage += rng.sample(autres, min(n - moitie, len(autres)))
    rng.shuffle(tirage)
    return tirage


def build_dpo_examples(records, splits):
    """Paires DPO : le prompt, la réponse préférée et la réponse écartée. Le split vient du
    découpage par cas. Les prompts sont des questions médicales, ils prennent la consigne
    de QA."""
    return [{**with_case_split(record, splits), "tache": "qa"} for record in records]


def sample_qa_examples(examples, n, seed=42):
    """Tire environ `n` exemples de QA, autant dans chaque langue, en gardant dans chaque
    langue les proportions des splits."""
    rng = random.Random(seed)
    par_strate = defaultdict(list)
    for example in examples:
        par_strate[(example["langue"], example["split"])].append(example)
    par_langue = Counter(example["langue"] for example in examples)

    echantillon = []
    for (langue, _), strate in sorted(par_strate.items()):
        fraction = n / len(par_langue) / par_langue[langue]
        echantillon += rng.sample(strate, round(len(strate) * fraction))
    return echantillon
