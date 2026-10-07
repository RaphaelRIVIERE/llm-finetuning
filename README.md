# Agent IA de triage médical

POC d'un agent de triage aux urgences pour le CHSA (mission OpenClassrooms, AI Engineer).
Le modèle lit la description d'un patient et renvoie un JSON : niveau d'urgence,
spécialité, symptômes, signes d'alerte, justification et recommandation.

Qwen3-1.7B-Base, fine tuné par SFT + LoRA puis aligné par DPO, servi par vLLM derrière une
API FastAPI.

**Prototype de recherche : il ne doit pas servir à trier de vrais patients.**

- Modèle : [rriviere/triage-chsa-qwen3-1.7b](https://huggingface.co/rriviere/triage-chsa-qwen3-1.7b),
  model card dans [docs/model_card.md](docs/model_card.md) (entraînement, résultats,
  limites)
- Dataset : [rriviere/oc-llm-finetuning-dataset](https://huggingface.co/datasets/rriviere/oc-llm-finetuning-dataset),
  dataset card dans [docs/dataset_card.md](docs/dataset_card.md)

## Structure du projet

- `app/` : l'API FastAPI (prompt, appel à vLLM, validation du JSON, traçabilité en base)
- `scripts/` : préparation des données, entraînement, évaluation, publication, mesures
- `notebooks/` : les étapes du projet, de l'exploration des sources à la comparaison des
  modèles
- `tests/` : tests Pytest
- `docs/` : dataset card, model card, protocole de triage, schéma des métadonnées, sources
- `modal_app.py` : déploiement sur Modal
- `Dockerfile`, `docker-compose.yml` : image de l'API et lancement en local

## Installation

Python 3.12 et [uv](https://docs.astral.sh/uv/).

```bash
uv sync
cp .env.example .env  # puis remplir les valeurs
```

## Lancer l'API en local

Il faut un GPU NVIDIA, Docker avec le support GPU, et le modèle fusionné dans `runs/final`.
Pour le récupérer depuis Hugging Face :

```bash
uv run hf download rriviere/triage-chsa-qwen3-1.7b --local-dir runs/final
```

Puis :

```bash
docker compose up --build
```

L'API répond sur http://localhost:8000, avec une base Postgres locale. Le démarrage prend
une à deux minutes (chargement du modèle et préparation de vLLM). La documentation
interactive est sur http://localhost:8000/docs.

## Utiliser l'API

`POST /triage`, avec la clé `API_KEY` du `.env` dans l'en-tête `X-API-Key` :

```bash
curl -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <clé>" \
  -d '{"instruction": "Femme de 72 ans, depuis 45 minutes elle ne bouge plus le bras droit, sa bouche est déviée et elle parle mal. Tension 185/100."}'
```

Exemple de réponse :

```json
{
  "urgency_level": "maximum",
  "specialty": "neurology",
  "key_symptoms": [
    "déficit moteur du bras droit",
    "déviation de la bouche",
    "trouble de la parole"
  ],
  "red_flags": ["suspicion d'accident vasculaire cérébral", "début depuis 45 minutes"],
  "justification": "...",
  "recommendation": "...",
  "interaction_id": 12
}
```

- `urgency_level` : `maximum`, `moderate` ou `deferred`.
- `specialty` : une valeur parmi 10 (`cardiology`, `neurology`, `pulmonology`...).
- La justification et la recommandation sont écrites dans la langue du cas, français ou
  anglais.
- `interaction_id` permet de retrouver la requête et la réponse en base.

Codes d'erreur :

| Code | Cause                                                               |
| ---- | ------------------------------------------------------------------- |
| 401  | clé API absente ou fausse                                           |
| 422  | texte vide, fait seulement d'espaces, ou de plus de 4000 caractères |
| 502  | le modèle n'a pas produit un JSON valide : faire un triage manuel   |

`GET /health` répond `{"status": "ok"}` quand l'API est prête.

## Tests

```bash
uv run pytest
```

vLLM est remplacé par un faux moteur et Postgres par SQLite : les tests tournent sans GPU.
Le test d'intégration appelle une vraie API, il ne tourne que si `API_URL` est défini :

```bash
API_URL=http://localhost:8000 uv run pytest tests/test_integration.py
```

## Pipeline CI/CD

À chaque push sur `main`, GitHub Actions ([ci.yml](.github/workflows/ci.yml)) enchaîne :

1. `tests` : la suite Pytest ;
2. `build` : construction de l'image Docker et vérification que l'application s'importe ;
3. `deploy` : déploiement de l'API sur Modal, seulement si les deux premiers ont réussi.

La révision Hugging Face du modèle est fixée dans `modal_app.py`. Pour déployer un nouveau
modèle : le publier, mettre la nouvelle révision dans ce fichier et pousser sur `main`.

## Reproduire le modèle

Les étapes de préparation des données sont dans les notebooks 01 à 05. Ensuite :

```bash
# dataset SFT et DPO en JSONL
uv run python -m scripts.export
# SFT avec LoRA, puis DPO à partir du meilleur checkpoint SFT
uv run python -m scripts.train_sft --nom-run triage
uv run python -m scripts.train_dpo --taille-train 5000 --nom-run triage_5000
# fusion des deux adaptateurs dans runs/final
uv run python -m scripts.merge_model
# réponses sur le test, comparées dans le notebook 06
uv run python -m scripts.generation --nom sft_dpo --modele runs/final --split test
# publication sur Hugging Face
uv run python -m scripts.publish_model
```

Les hyperparamètres et les seeds sont dans les classes `Hyperparametres` de
`scripts/train_sft.py` et `scripts/train_dpo.py`, et rappelés dans la model card. Les runs
sont suivis dans MLflow (`uv run mlflow ui`).

Pour comparer la vitesse de vLLM et de transformers sur le même GPU :

```bash
uv run python -m scripts.benchmark_vllm --moteur vllm
uv run python -m scripts.benchmark_vllm --moteur transformers
```

Sur une machine WSL où FlashInfer ne compile pas, ajouter `VLLM_USE_FLASHINFER_SAMPLER=0`
devant les commandes qui lancent vLLM.
