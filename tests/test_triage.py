"""Tests du format JSON de triage et de la fonction de parsing."""

import json

from app.triage import (
    SortieTriage,
    Specialty,
    StatutParsing,
    UrgencyLevel,
    parser_sortie,
    vers_json,
)

SORTIE = {
    "urgency_level": "maximum",
    "specialty": "cardiology",
    "key_symptoms": ["douleur thoracique", "irradiation au bras gauche"],
    "red_flags": ["douleur thoracique chez un homme de 58 ans"],
    "justification": "Suspicion de syndrome coronarien aigu. Prise en charge immédiate.",
}
JSON_PROPRE = json.dumps(SORTIE, ensure_ascii=False)


def test_json_propre_est_valide():
    resultat = parser_sortie(JSON_PROPRE)
    assert resultat.statut == StatutParsing.VALIDE
    assert resultat.sortie.urgency_level == UrgencyLevel.MAXIMUM
    assert resultat.sortie.specialty == Specialty.CARDIOLOGY


def test_json_entoure_de_texte_est_valide():
    texte = f"Voici mon analyse :\n```json\n{JSON_PROPRE}\n```\nBonne journée."
    resultat = parser_sortie(texte)
    assert resultat.statut == StatutParsing.VALIDE
    assert resultat.sortie.model_dump(mode="json") == SORTIE


def test_accolade_parasite_avant_le_json():
    texte = "Format attendu {urgence}. Réponse : " + JSON_PROPRE
    assert parser_sortie(texte).statut == StatutParsing.VALIDE


def test_json_casse_est_invalide():
    # Sortie coupée en plein milieu, comme quand max_tokens est atteint.
    resultat = parser_sortie(JSON_PROPRE[:40])
    assert resultat.statut == StatutParsing.JSON_INVALIDE
    assert resultat.sortie is None


def test_texte_sans_json_est_invalide():
    assert parser_sortie("Syndrome coronarien aigu.").statut == StatutParsing.JSON_INVALIDE


def test_niveau_inconnu_est_hors_liste():
    sortie = {**SORTIE, "urgency_level": "urgent"}
    resultat = parser_sortie(json.dumps(sortie))
    assert resultat.statut == StatutParsing.VALEUR_HORS_LISTE
    assert resultat.sortie is None


def test_specialite_inconnue_est_hors_liste():
    sortie = {**SORTIE, "specialty": "pediatrics"}
    assert parser_sortie(json.dumps(sortie)).statut == StatutParsing.VALEUR_HORS_LISTE


def test_cle_manquante_est_schema_invalide():
    sortie = {k: v for k, v in SORTIE.items() if k != "red_flags"}
    assert parser_sortie(json.dumps(sortie)).statut == StatutParsing.SCHEMA_INVALIDE


def test_cle_en_trop_est_schema_invalide():
    sortie = {**SORTIE, "diagnostic": "SCA"}
    assert parser_sortie(json.dumps(sortie)).statut == StatutParsing.SCHEMA_INVALIDE


def test_mauvais_type_est_schema_invalide():
    sortie = {**SORTIE, "key_symptoms": "douleur thoracique"}
    assert parser_sortie(json.dumps(sortie)).statut == StatutParsing.SCHEMA_INVALIDE


def test_champ_vide_est_schema_invalide():
    for champ, vide in [("key_symptoms", []), ("justification", "")]:
        sortie = {**SORTIE, champ: vide}
        assert parser_sortie(json.dumps(sortie)).statut == StatutParsing.SCHEMA_INVALIDE


def test_red_flags_vide_est_valide():
    sortie = {**SORTIE, "urgency_level": "deferred", "red_flags": []}
    assert parser_sortie(json.dumps(sortie)).statut == StatutParsing.VALIDE


def test_erreur_de_schema_passe_avant_valeur_hors_liste():
    # Clé manquante et niveau inconnu en même temps : c'est la structure qui compte.
    sortie = {k: v for k, v in SORTIE.items() if k != "red_flags"}
    sortie["urgency_level"] = "urgent"
    assert parser_sortie(json.dumps(sortie)).statut == StatutParsing.SCHEMA_INVALIDE


def test_vers_json_garde_l_ordre_et_les_accents():
    texte = vers_json(SortieTriage.model_validate(SORTIE))
    assert texte.startswith('{"urgency_level": "maximum"')
    assert "immédiate" in texte
    assert parser_sortie(texte).statut == StatutParsing.VALIDE


def test_niveau_s_ecrit_comme_sa_valeur():
    assert f"{UrgencyLevel.MAXIMUM}" == "maximum"
