"""Tests de l'API de triage, avec vLLM et Postgres remplacés (voir conftest.py)."""

from app.config import PARAMETRES_DECODAGE
from app.models import Interaction, Log
from tests.constantes import REPONSE_FACTICE

INSTRUCTION = "Homme de 58 ans, douleur thoracique irradiant dans le bras gauche."


def test_sante(client):
    reponse = client.get("/sante")
    assert reponse.status_code == 200
    assert reponse.json() == {"statut": "ok"}


def test_triage_renvoie_la_reponse_du_modele(client):
    reponse = client.post("/triage", json={"instruction": INSTRUCTION})
    assert reponse.status_code == 200
    assert reponse.json() == {"reponse": REPONSE_FACTICE}


def test_triage_utilise_les_parametres_de_decodage_de_la_config(client, faux_moteur):
    client.post("/triage", json={"instruction": INSTRUCTION})
    appel = faux_moteur.appels[-1]
    assert appel.prompt == INSTRUCTION
    assert vars(appel.params) == PARAMETRES_DECODAGE


# La base est partagée par tous les tests de la session. On compte les lignes avant
# l'appel pour ne regarder que celles ajoutées par le test lui même.


def test_triage_enregistre_l_interaction_et_le_log(client, lire_table):
    nb_interactions = len(lire_table(Interaction))
    nb_logs = len(lire_table(Log))

    client.post("/triage", json={"instruction": INSTRUCTION})

    nouvelles_interactions = lire_table(Interaction)[nb_interactions:]
    assert len(nouvelles_interactions) == 1
    interaction = nouvelles_interactions[0]
    assert interaction.instruction == INSTRUCTION
    assert interaction.response == REPONSE_FACTICE
    assert interaction.generation_time_ms > 0

    nouveaux_logs = lire_table(Log)[nb_logs:]
    assert len(nouveaux_logs) == 1
    log = nouveaux_logs[0]
    assert log.method == "POST"
    assert log.path == "/triage"
    assert log.status_code == 200
    assert log.interaction_id == interaction.id
    assert log.error_detail is None


def test_requete_invalide_est_journalisee_avec_l_erreur(client, lire_table):
    nb_interactions = len(lire_table(Interaction))
    nb_logs = len(lire_table(Log))

    reponse = client.post("/triage", json={})

    assert reponse.status_code == 422
    assert len(lire_table(Interaction)) == nb_interactions
    nouveaux_logs = lire_table(Log)[nb_logs:]
    assert len(nouveaux_logs) == 1
    log = nouveaux_logs[0]
    assert log.status_code == 422
    assert log.interaction_id is None
    assert "instruction" in log.error_detail


def test_moteur_sans_sortie_renvoie_500_et_est_journalise(client, faux_moteur, lire_table, monkeypatch):
    monkeypatch.setattr(faux_moteur, "vide", True)
    nb_interactions = len(lire_table(Interaction))
    nb_logs = len(lire_table(Log))

    reponse = client.post("/triage", json={"instruction": INSTRUCTION})

    assert reponse.status_code == 500
    assert "aucune sortie" in reponse.json()["detail"]
    assert len(lire_table(Interaction)) == nb_interactions
    nouveaux_logs = lire_table(Log)[nb_logs:]
    assert len(nouveaux_logs) == 1
    log = nouveaux_logs[0]
    assert log.status_code == 500
    assert log.interaction_id is None
    assert "aucune sortie" in log.error_detail
