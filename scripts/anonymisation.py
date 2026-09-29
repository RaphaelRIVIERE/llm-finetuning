"""Anonymisation des sources françaises (MediQAl, FrenchMedMCQA). Détails dans le
notebook 02.

Un nom écrit sans titre, sans initiale et sans âge juste après peut passer à travers.
"""

from scripts.patient_names import find_leftover_names, replace_patient_names

SOURCES_FRANCAISES = ("mediqal", "frenchmedmcqa")


def anonymize_text(text):
    """Renvoie (texte anonymisé, modifié ou pas), ou None s'il reste un nom."""
    text, touche = replace_patient_names(text)
    if find_leftover_names(text, "fr"):
        return None
    return text, touche


def anonymize_french_sources(records):
    """Anonymise les records français et supprime ceux où il reste un nom."""
    gardes = []
    for record in records:
        if record["source"] not in SOURCES_FRANCAISES:
            gardes.append(record)
            continue
        instruction = anonymize_text(record["instruction"])
        reponse = anonymize_text(record["reponse"])
        if instruction is None or reponse is None:
            continue
        record["instruction"], touche_i = instruction
        record["reponse"], touche_r = reponse
        if touche_i or touche_r:
            record["transformations"].append("anonymisation_noms")
        gardes.append(record)
    return gardes
