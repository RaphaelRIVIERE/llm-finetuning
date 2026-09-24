FROM python:3.12-slim

# Triton et torch.compile (utilisés par vLLM au démarrage) compilent du C à la volée.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libc6-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.12.7 /uv /bin/uv

WORKDIR /app

# Dépendances installées avant de copier le code, pour garder cette couche (plusieurs Go)
# en cache tant que uv.lock ne change pas. Seulement le groupe serving, pas l'entraînement.
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-default-groups --group serving

COPY app ./app

ENV PATH="/app/.venv/bin:$PATH"
# Les bibliothèques CUDA 13 arrivent avec torch mais pas sur le chemin du chargeur
# dynamique (voir docs/decisions.md).
ENV LD_LIBRARY_PATH="/app/.venv/lib/python3.12/site-packages/nvidia/cu13/lib"
# FlashInfer compile ses kernels à la volée et échoue sans nvcc. vLLM retombe alors sur
# son échantillonnage standard.
ENV VLLM_USE_FLASHINFER_SAMPLER=0
# Le modèle n'est pas dans l'image : on le monte ici, ou on met un identifiant Hugging Face.
ENV CHEMIN_MODELE=/modele

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
