"""Anonymise MediQAl et FrenchMedMCQA : les noms de patients deviennent [PATIENT]. Détails
dans le notebook 02.

Limite : un nom écrit sans titre, sans initiale et sans âge juste après peut passer.
"""

from scripts.patient_names import find_leftover_names, replace_patient_names

SOURCES_FRANCAISES = ("mediqal", "frenchmedmcqa")


def anonymize_french_sources(records):
    """Remplace les noms dans instruction et reponse, et supprime les records où un nom
    reste repéré. Les autres sources passent sans changement."""
    gardes = []
    for record in records:
        if record["source"] not in SOURCES_FRANCAISES:
            gardes.append(record)
            continue
        instruction, touche_i = replace_patient_names(record["instruction"])
        reponse, touche_r = replace_patient_names(record["reponse"])
        if find_leftover_names(instruction, "fr") or find_leftover_names(reponse, "fr"):
            continue
        record["instruction"] = instruction
        record["reponse"] = reponse
        if touche_i or touche_r:
            record["transformations"].append("anonymisation_noms")
        gardes.append(record)
    return gardes
