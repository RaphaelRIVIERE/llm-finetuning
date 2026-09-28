"""Unité de cas de chaque source, utilisée pour le dédoublonnage, le découpage et le
contrôle de fuite. Pas de dépendance lourde ici, pour que les tests tournent dans la CI.

Ce qu'est un cas selon la source :
- MediQAl : le texte du cas clinique (plusieurs questions portent sur le même cas).
  Sans cas clinique, la question seule.
- MedQuAD et FrenchMedMCQA : la question.
- UltraMedical-Preference : le prompt.
"""

import re
import unicodedata

ESPACES = re.compile(r"\s+")


def normaliser_texte(texte):
    """Met le texte sous une forme stable pour comparer deux cas : unicode normalisé,
    minuscules, espaces multiples et retours à la ligne ramenés à un seul espace."""
    texte = unicodedata.normalize("NFKC", texte)
    texte = ESPACES.sub(" ", texte)
    return texte.strip().casefold()
