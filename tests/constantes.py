"""Valeurs partagées entre conftest.py et les tests."""

import json

# Une sortie de triage valide, sur une ligne comme celles du modèle.
SORTIE_FACTICE = {
    "urgency_level": "maximum",
    "specialty": "cardiology",
    "key_symptoms": ["douleur thoracique", "irradiation dans le bras gauche"],
    "red_flags": ["suspicion de syndrome coronarien aigu"],
    "justification": "Douleur thoracique typique chez un homme de 58 ans.",
    "recommendation": "Prise en charge immédiate en salle de déchocage.",
}
REPONSE_FACTICE = json.dumps(SORTIE_FACTICE, ensure_ascii=False)

CLE_API = "cle-de-test"
ENTETES = {"X-API-Key": CLE_API}
