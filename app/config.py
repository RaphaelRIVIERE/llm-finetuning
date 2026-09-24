"""Réglages du service de triage, regroupés ici pour n'avoir qu'un endroit à modifier."""

import os

CHEMIN_MODELE = os.environ.get("CHEMIN_MODELE", "runs/final")

# Clé attendue dans le header X-API-Key pour appeler /triage. Pas de valeur par défaut :
# l'API refuse de démarrer sans elle.
API_KEY = os.environ.get("API_KEY")

URL_BASE = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg://triage:triage@localhost:5432/triage"
)

# Défaut vLLM (~0.9) trop haut sur un GPU 8 Go partagé avec le reste du système (WSL).
GPU_MEMORY_UTILIZATION = float(os.environ.get("GPU_MEMORY_UTILIZATION", "0.8"))
# Défaut du modèle (32768) réserve plus de cache KV que ce qu'il reste de VRAM après
# le chargement des poids. Les instructions et réponses de triage sont courtes.
MAX_MODEL_LEN = int(os.environ.get("MAX_MODEL_LEN", "4096"))

# Passés tels quels à SamplingParams. frequency_penalty remplace le couple
# repetition_penalty + no_repeat_ngram_size de l'évaluation Transformers, choix testé
# dans scripts/test_decodage.py (voir docs/experimentations.md).
PARAMETRES_DECODAGE = dict(
    max_tokens=512,
    temperature=0.0,
    frequency_penalty=0.5,
)
