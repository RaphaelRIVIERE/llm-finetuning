"""Scores de triage : compare les niveaux attendus aux réponses d'un modèle.

La même fonction sert pour tous les modèles comparés (classe majoritaire, baseline few
shot, SFT, SFT+DPO). Seule la façon d'obtenir les réponses change.
"""

from sklearn.metrics import confusion_matrix, f1_score

from app.triage import UrgencyLevel, parser_sortie

NIVEAUX = [niveau.value for niveau in UrgencyLevel]
# Prédiction d'une réponse dont on ne peut pas lire le niveau (JSON cassé, schéma faux)
INVALIDE = "invalide"
# Du plus urgent au moins urgent. Une réponse invalide ne donne aucun niveau à
# l'équipe : le patient attend, c'est comme un deferred.
RANG = {"maximum": 0, "moderate": 1, "deferred": 2, INVALIDE: 2}


def niveau_predit(reponse):
    """Niveau d'urgence lu dans la réponse du modèle, ou INVALIDE."""
    resultat = parser_sortie(reponse)
    if resultat.sortie is None:
        return INVALIDE
    return resultat.sortie.urgency_level.value


def scores_triage(attendus, reponses):
    """Scores d'un modèle sur un jeu de cas. `attendus` : niveaux relus à la main,
    `reponses` : textes bruts produits par le modèle, dans le même ordre."""
    predits = [niveau_predit(reponse) for reponse in reponses]
    # Une réponse invalide n'est jamais un bon niveau : elle compte comme une erreur
    # pour la classe attendue
    f1 = f1_score(attendus, predits, labels=NIVEAUX, average=None, zero_division=0)
    matrice = confusion_matrix(attendus, predits, labels=NIVEAUX + [INVALIDE])
    sous_triage = sum(RANG[p] > RANG[a] for a, p in zip(attendus, predits))
    # Rappel sur maximum : parmi les vraies urgences vitales, la part trouvée
    predits_si_maximum = [p for a, p in zip(attendus, predits) if a == "maximum"]
    return {
        "n": len(attendus),
        "json_valide": sum(p != INVALIDE for p in predits) / len(predits),
        "f1_par_classe": dict(zip(NIVEAUX, f1.tolist())),
        "f1_macro": float(f1.mean()),
        "rappel_maximum": predits_si_maximum.count("maximum") / len(predits_si_maximum) if predits_si_maximum else None,
        "sous_triage": sous_triage / len(attendus),
        # Lignes : niveau attendu. Colonnes : niveau prédit, plus INVALIDE en dernier.
        # La ligne INVALIDE est retirée, ce n'est jamais un niveau attendu.
        "matrice": matrice[:len(NIVEAUX)].tolist(),
    }


def scores_par_langue(attendus, reponses, langues):
    """Scores sur tout le jeu, puis séparés par langue."""
    scores = {"tous": scores_triage(attendus, reponses)}
    for langue in sorted(set(langues)):
        garde = [i for i, l in enumerate(langues) if l == langue]
        scores[langue] = scores_triage([attendus[i] for i in garde], [reponses[i] for i in garde])
    return scores
