"""Tests de la normalisation des cas."""

from scripts.cas import normaliser_texte


def test_majuscules_et_espaces_ignores():
    a = "Une femme de 52 ans  consulte\npour une prise de poids."
    b = "une femme de 52 ans consulte pour une prise de poids. "
    assert normaliser_texte(a) == normaliser_texte(b)


def test_espace_insecable_ignore():
    assert normaliser_texte("52 ans") == normaliser_texte("52 ans")


def test_textes_differents_restent_differents():
    assert normaliser_texte("Homme de 58 ans") != normaliser_texte("Homme de 85 ans")
