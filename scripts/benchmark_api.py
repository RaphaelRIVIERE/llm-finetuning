"""Mesure la latence et le débit de l'API de triage déployée, vus du client.

    uv run python -m scripts.benchmark_api --url <URL_API>
"""

import argparse
import asyncio
import json
import os
import random
import statistics
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

FICHIER_TEST = Path("data/export/sft/test.jsonl")
DOSSIER_SORTIE = Path("data/benchmark")
# Le démarrage à froid prend 1 à 3 minutes : large marge avant d'abandonner un appel.
DELAI_MAX = 600


def lire_cas(nb_cas, seed):
    with open(FICHIER_TEST, encoding="utf-8") as f:
        cas = [ex["instruction"] for ex in map(json.loads, f) if ex["tache"] == "triage"]
    random.Random(seed).shuffle(cas)
    return cas[:nb_cas]


async def appeler(client, url, cle, cas):
    debut = time.perf_counter()
    reponse = await client.post(f"{url}/triage", json={"instruction": cas}, headers={"X-API-Key": cle})
    latence_ms = (time.perf_counter() - debut) * 1000
    # Une erreur de Modal (démarrage raté, délai dépassé) peut ne pas renvoyer de JSON.
    corps = reponse.json() if reponse.headers.get("content-type", "").startswith("application/json") else {}
    return {"statut": reponse.status_code, "latence_ms": latence_ms, "interaction_id": corps.get("interaction_id")}


async def mesurer(client, url, cle, tous_les_cas, concurrence):
    """Envoie tous les cas, avec au plus `concurrence` requêtes en cours à la fois."""
    limite = asyncio.Semaphore(concurrence)

    async def appeler_avec_limite(cas):
        async with limite:
            return await appeler(client, url, cle, cas)

    debut = time.perf_counter()
    resultats = await asyncio.gather(*(appeler_avec_limite(cas) for cas in tous_les_cas))
    duree_s = time.perf_counter() - debut
    return resultats, duree_s


def resumer(resultats, duree_s):
    latences = sorted(r["latence_ms"] for r in resultats)
    return {
        "requetes": len(resultats),
        "erreurs": sum(r["statut"] != 200 for r in resultats),
        "duree_s": round(duree_s, 1),
        "requetes_par_s": round(len(resultats) / duree_s, 2),
        "latence_mediane_ms": round(statistics.median(latences)),
        "latence_p95_ms": round(latences[int(0.95 * (len(latences) - 1))]),
    }


async def main(url, nb_cas, concurrences, seed):
    load_dotenv()
    cle = os.environ["API_KEY"]
    tous_les_cas = lire_cas(nb_cas, seed)

    # Modal répond 303 à une requête qui dépasse 150 s (démarrage à froid) et donne une
    # adresse où attendre la réponse : il faut suivre la redirection.
    async with httpx.AsyncClient(timeout=DELAI_MAX, follow_redirects=True) as client:
        premier = await appeler(client, url, cle, tous_les_cas[0])
        print(f"premier appel (à froid si l'API dormait) : {premier['latence_ms'] / 1000:.1f} s, statut {premier['statut']}")

        mesures = {}
        for concurrence in concurrences:
            resultats, duree_s = await mesurer(client, url, cle, tous_les_cas, concurrence)
            mesures[concurrence] = {"resume": resumer(resultats, duree_s), "requetes": resultats}
            print(f"concurrence {concurrence} : {mesures[concurrence]['resume']}")

    DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)
    chemin = DOSSIER_SORTIE / f"api_{time.strftime('%Y%m%d_%H%M%S')}.json"
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump({"url": url, "nb_cas": nb_cas, "seed": seed, "premier_appel": premier, "mesures": mesures}, f, indent=2)
    print(f"résultats : {chemin}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="adresse de l'API, sans / final")
    parser.add_argument("--nb-cas", type=int, default=48)
    parser.add_argument("--concurrences", type=int, nargs="+", default=[1, 8, 32])
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    asyncio.run(main(args.url, args.nb_cas, args.concurrences, args.seed))
