"""Déploie l'API de triage sur Modal, avec un GPU L4 (ou A10G si aucun L4 n'est libre).

L'image est construite à partir du Dockerfile : c'est la même que celle testée en local
et dans le pipeline. Le modèle n'est pas dans l'image, vLLM le télécharge depuis Hugging
Face au démarrage, à la révision fixée plus bas.

Déployer : modal deploy modal_app.py

Le secret Modal « triage-chsa » doit contenir API_KEY, DATABASE_URL (Neon) et HF_TOKEN.
"""

import subprocess

import modal

MODELE = "rriviere/triage-chsa-qwen3-1.7b"
# Commit du modèle sur Hugging Face. Pour déployer un nouveau modèle : le publier
# (scripts/publish_model.py), mettre ici la révision affichée et pousser sur main. Le
# pipeline relance alors les tests puis redéploie.
REVISION_MODELE = "7805dcd4b5d91b127d6b5ffad004855fcfe5ed24"

MINUTES = 60

app = modal.App("triage-chsa")
image = modal.Image.from_dockerfile("Dockerfile")
# Garde le modèle téléchargé et le cache de compilation de vLLM entre deux démarrages.
# Monté sur un dossier vide : Modal refuse /root/.cache, déjà rempli dans l'image par uv.
cache = modal.Volume.from_name("triage-chsa-cache", create_if_missing=True)
DOSSIER_CACHE = "/cache"


@app.function(
    image=image,
    # L4 en premier choix. Les L4 manquent parfois (12 minutes d'attente mesurées le
    # 2026-10-06) : Modal prend alors un A10G, 24 Go aussi et compatible bfloat16.
    gpu=["L4", "A10G"],
    secrets=[modal.Secret.from_name("triage-chsa")],
    env={
        "CHEMIN_MODELE": MODELE,
        "REVISION_MODELE": REVISION_MODELE,
        "HF_HOME": f"{DOSSIER_CACHE}/huggingface",
        "VLLM_CACHE_ROOT": f"{DOSSIER_CACHE}/vllm",
    },
    volumes={DOSSIER_CACHE: cache},
    # Le conteneur s'éteint après 5 minutes sans requête : rien n'est facturé à l'arrêt.
    scaledown_window=5 * MINUTES,
    # Un seul GPU au plus, pour ne pas dépasser le crédit gratuit.
    max_containers=1,
    timeout=10 * MINUTES,
)
# Plusieurs requêtes en même temps sur le même conteneur : vLLM les traite par lots.
@modal.concurrent(max_inputs=32)
# Téléchargement du modèle et démarrage de vLLM avant que l'API réponde.
@modal.web_server(8000, startup_timeout=10 * MINUTES)
def api():
    # La même commande que le CMD du Dockerfile, que Modal n'exécute pas.
    subprocess.Popen(["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"], cwd="/app")
