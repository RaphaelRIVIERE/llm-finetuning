"""Anonymisation ciblée de MediQAl.

Seule MediQAl contient de vrais noms de patients, sous la forme prénom +
initiale (« Jean X. ») ou titre + initiale (« Monsieur D. »). Voir
notebooks/04_exploration_anonymisation.ipynb pour l'exploration qui justifie
ce choix.

Deux passes : un motif titre + initiale par regex direct, parce que Presidio
en rate une grande partie, puis Presidio filtré sur le motif prénom +
initiale pour les cas sans titre, où un regex direct produirait trop de faux
positifs (« Streptocoque A. » a la même forme que « Brigitte V. »).

Limite connue : un prénom sans titre que Presidio ne détecte pas comme
PERSON peut passer à travers ces deux passes.
"""

import re

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

MOTIF_NOM_PATIENT = re.compile(r"^[A-ZÉÈÀÂÎÔÛÏÜÖÇ][a-zàâéèêëîïôûùç]+ [A-Z]\.?$")
MOTIF_TITRE_INITIALE = re.compile(r"\b(Monsieur|Madame|Mademoiselle|Mme|Mr|M)\.?\s+[A-ZÉÈÀÂÎÔÛÏÜÖÇ]\.")


def build_analyzer():
    config = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "fr", "model_name": "fr_core_news_md"}],
    }
    provider = NlpEngineProvider(nlp_configuration=config)
    return AnalyzerEngine(nlp_engine=provider.create_engine(), supported_languages=["fr"])


def anonymize_text(text, analyzer, anonymizer):
    """Remplace par [PATIENT] les patients désignés par titre + initiale (regex
    direct) puis par prénom + initiale (détection PERSON de Presidio filtrée sur
    le motif). Renvoie le texte et un booléen indiquant si une substitution a eu
    lieu, dans l'une ou l'autre passe."""
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
    """Anonymise en place les champs instruction/reponse des records dont
    `source` vaut 'mediqal' (les autres records de la liste sont ignorés).
    Ajoute 'anonymisation_presidio' à `transformations` sur les records touchés."""
    analyzer = build_analyzer()
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
