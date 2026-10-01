"""Prompts envoyés au modèle. Le dataset garde le texte seul (cas ou question) : la
consigne est ajoutée ici, au même endroit pour l'entraînement, l'évaluation et l'API."""

from app.triage import Specialty, UrgencyLevel


def enumerer(valeurs):
    """Écrit les valeurs d'une liste fermée : « a, b ou c »."""
    valeurs = [valeur.value for valeur in valeurs]
    return ", ".join(valeurs[:-1]) + " ou " + valeurs[-1]


# Une seule consigne, en français, pour les cas français et anglais : l'API n'a pas à
# deviner la langue du patient. La réponse suit la langue du cas : pour les cas anglais,
# les champs texte des labels ont été traduits (scripts/traduction.py).
CONSIGNE_TRIAGE = f"""Tu fais le triage d'un patient à l'accueil des urgences. Réponds uniquement avec un objet JSON qui a ces clés, dans cet ordre :
- "urgency_level" : {enumerer(UrgencyLevel)}
- "specialty" : {enumerer(Specialty)}
- "key_symptoms" : liste de chaînes courtes
- "red_flags" : liste de chaînes courtes, vide s'il n'y en a pas
- "justification" : 2 ou 3 phrases, dans la langue du cas
- "recommendation" : une phrase courte, dans la langue du cas"""

CONSIGNE_QA = "Réponds à la question médicale suivante, dans la langue de la question."

# Pour chaque tâche : la consigne et le nom donné au texte dans le prompt
TACHES = {
    "triage": (CONSIGNE_TRIAGE, "Cas"),
    "qa": (CONSIGNE_QA, "Question"),
}


def construire_prompt(tache, texte):
    """Prompt complet d'une tâche (`triage` ou `qa`). La réponse du modèle vient juste
    après."""
    consigne, nom = TACHES[tache]
    return f"{consigne}\n\n{nom} : {texte}\n\nRéponse :\n"
