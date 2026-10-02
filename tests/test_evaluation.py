"""Tests des scores de triage, avec de fausses réponses de modèle."""

import json

from scripts.evaluation import INVALIDE, niveau_lu, niveau_predit, scores_par_langue, scores_triage


def reponse(niveau):
    """Réponse de modèle bien formée, avec le niveau donné."""
    return json.dumps({
        "urgency_level": niveau,
        "specialty": "general_medicine",
        "key_symptoms": ["fièvre"],
        "red_flags": [],
        "justification": "Justification.",
        "recommendation": "Recommandation.",
    })


JSON_CASSE = '{"urgency_level": "maximum", "specialty":'


def test_niveau_lu_dans_la_reponse():
    assert niveau_predit("Voici le triage : " + reponse("moderate")) == "moderate"


def test_json_casse_donne_invalide():
    assert niveau_predit(JSON_CASSE) == INVALIDE


def test_modele_parfait():
    attendus = ["maximum", "moderate", "deferred"]
    scores = scores_triage(attendus, [reponse(n) for n in attendus])
    assert scores["json_valide"] == 1
    assert scores["f1_macro"] == 1
    assert scores["rappel_maximum"] == 1
    assert scores["sous_triage"] == 0


def test_json_casse_sur_une_urgence_est_une_urgence_ratee():
    attendus = ["maximum", "maximum", "deferred"]
    reponses = [reponse("maximum"), JSON_CASSE, reponse("deferred")]
    scores = scores_triage(attendus, reponses)
    assert scores["json_valide"] == 2 / 3
    assert scores["rappel_maximum"] == 1 / 2
    assert scores["sous_triage"] == 1 / 3
    # Ligne maximum : 1 bien classé, 1 invalide (dernière colonne)
    assert scores["matrice"][0] == [1, 0, 0, 1]


def test_surestimer_n_est_pas_du_sous_triage():
    attendus = ["deferred", "moderate"]
    reponses = [reponse("maximum"), reponse("maximum")]
    scores = scores_triage(attendus, reponses)
    assert scores["sous_triage"] == 0
    assert scores["f1_macro"] == 0


def test_scores_separes_par_langue():
    attendus = ["maximum", "maximum"]
    reponses = [reponse("maximum"), reponse("deferred")]
    scores = scores_par_langue(attendus, reponses, ["fr", "en"])
    assert scores["tous"]["rappel_maximum"] == 1 / 2
    assert scores["fr"]["rappel_maximum"] == 1
    assert scores["en"]["rappel_maximum"] == 0


def test_niveau_lu_malgre_une_specialite_hors_liste():
    hors_liste = reponse("moderate").replace("general_medicine", "pediatrics")
    assert niveau_predit(hors_liste) == INVALIDE
    assert niveau_lu(hors_liste) == "moderate"


def test_niveau_lu_reste_invalide_sans_niveau_connu():
    assert niveau_lu(JSON_CASSE) == INVALIDE
    assert niveau_lu(reponse("critique")) == INVALIDE
