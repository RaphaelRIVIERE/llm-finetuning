"""Anonymisation ciblée de MediQAl (noms de patients) et d'UltraMedical-
Preference (emails, téléphones personnels). FrenchMedMCQA et MedQuAD n'ont
rien à anonymiser. Détail et justification :
notebooks/04_exploration_anonymisation.ipynb.

Limite connue : un prénom sans titre que Presidio ne détecte pas comme
PERSON peut passer à travers les deux passes MediQAl.
"""

import re

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

MOTIF_NOM_PATIENT = re.compile(r"^[A-ZÉÈÀÂÎÔÛÏÜÖÇ][a-zàâéèêëîïôûùç]+ [A-Z]\.?$")
MOTIF_TITRE_INITIALE = re.compile(r"\b(Monsieur|Madame|Mademoiselle|Mme|Mr|M)\.?\s+[A-ZÉÈÀÂÎÔÛÏÜÖÇ]\.")

MODELES_SPACY = {"fr": "fr_core_news_md", "en": "en_core_web_md"}


def build_analyzer(langue="fr"):
    config = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": langue, "model_name": MODELES_SPACY[langue]}],
    }
    provider = NlpEngineProvider(nlp_configuration=config)
    return AnalyzerEngine(nlp_engine=provider.create_engine(), supported_languages=[langue])


def anonymize_text(text, analyzer, anonymizer):
    """Remplace par [PATIENT] les patients désignés par titre + initiale ou
    prénom + initiale. Renvoie le texte et un booléen (substitution ou pas)."""
    text, titre_touche = MOTIF_TITRE_INITIALE.subn(r"\1 [PATIENT]", text)
    titre_touche = titre_touche > 0

    resultats = analyzer.analyze(text=text, language="fr", entities=["PERSON"])
    a_anonymiser = [r for r in resultats if MOTIF_NOM_PATIENT.match(text[r.start:r.end].strip())]
    if not a_anonymiser:
        return text, titre_touche
    resultat = anonymizer.anonymize(
        text=text,
        analyzer_results=a_anonymiser,
        operators={"PERSON": OperatorConfig("replace", {"new_value": "[PATIENT]"})},
    )
    return resultat.text, True


def anonymize_mediqal(records):
    """Anonymise en place instruction/reponse des records mediqal. Ajoute
    'anonymisation_presidio' à `transformations` sur les records touchés."""
    analyzer = build_analyzer("fr")
    anonymizer = AnonymizerEngine()
    for record in records:
        if record["source"] != "mediqal":
            continue
        instruction, touche_i = anonymize_text(record["instruction"], analyzer, anonymizer)
        reponse, touche_r = anonymize_text(record["reponse"], analyzer, anonymizer)
        record["instruction"] = instruction
        record["reponse"] = reponse
        if touche_i or touche_r:
            record["transformations"].append("anonymisation_presidio")
    return records


def anonymize_contact_info(text, analyzer, anonymizer):
    """Remplace par [EMAIL]/[TELEPHONE] les emails et numéros de téléphone
    détectés par Presidio."""
    resultats = analyzer.analyze(text=text, language="en", entities=["EMAIL_ADDRESS", "PHONE_NUMBER"])
    if not resultats:
        return text, False
    resultat = anonymizer.anonymize(
        text=text,
        analyzer_results=resultats,
        operators={
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[EMAIL]"}),
            "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[TELEPHONE]"}),
        },
    )
    return resultat.text, True


def anonymize_ultramedical_preference(records):
    """Anonymise en place prompt/chosen/rejected des records
    ultramedical_preference. Ajoute 'anonymisation_presidio' à
    `transformations` sur les records touchés."""
    analyzer = build_analyzer("en")
    anonymizer = AnonymizerEngine()
    for record in records:
        if record["source"] != "ultramedical_preference":
            continue
        touche = False
        for champ in ("prompt", "chosen", "rejected"):
            nouveau_texte, ce_champ_touche = anonymize_contact_info(record[champ], analyzer, anonymizer)
            record[champ] = nouveau_texte
            touche = touche or ce_champ_touche
        if touche:
            record["transformations"].append("anonymisation_presidio")
    return records
