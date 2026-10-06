"""Réglages du service de triage, regroupés ici pour n'avoir qu'un endroit à modifier."""

import os

CHEMIN_MODELE = os.environ.get("CHEMIN_MODELE", "runs/final")
# Révision Hugging Face du modèle (commit). Rien en local, où le modèle est un dossier.
REVISION_MODELE = os.environ.get("REVISION_MODELE")
# Enregistrée avec chaque interaction, pour savoir quel modèle a répondu.
VERSION_MODELE = f"{CHEMIN_MODELE}@{REVISION_MODELE}" if REVISION_MODELE else CHEMIN_MODELE

# Clé attendue dans le header X-API-Key pour appeler /triage. Pas de valeur par défaut :
# l'API refuse de démarrer sans elle.
API_KEY = os.environ.get("API_KEY")

URL_BASE = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg://triage:triage@localhost:5432/triage"
)

# bfloat16 conseillé par vLLM sur GPU comme sur CPU (float16 instable sur CPU).
DTYPE = os.environ.get("DTYPE", "bfloat16")

# Défaut vLLM (~0.9) trop haut sur un GPU 8 Go partagé avec le reste du système (WSL).
GPU_MEMORY_UTILIZATION = float(os.environ.get("GPU_MEMORY_UTILIZATION", "0.8"))
# Défaut du modèle (32768) réserve plus de cache KV que ce qu'il reste de VRAM après
# le chargement des poids. Les instructions et réponses de triage sont courtes.
MAX_MODEL_LEN = int(os.environ.get("MAX_MODEL_LEN", "4096"))

# Le plus long cas du dataset fait environ 4000 caractères. Avec la consigne et les 512
# tokens de réponse, ça tient largement dans MAX_MODEL_LEN.
LONGUEUR_MAX_CAS = 4000

# Passés tels quels à SamplingParams, ici et dans scripts/generation.py : l'API décode
# comme l'évaluation. Glouton et sans pénalité : une pénalité de fréquence abîmerait le
# JSON, qui répète forcément guillemets et deux points. Le JSON d'entraînement tient sur
# une seule ligne : on arrête au premier retour à la ligne.
PARAMETRES_DECODAGE = dict(
    max_tokens=512,
    temperature=0.0,
    stop=["\n"],
)
