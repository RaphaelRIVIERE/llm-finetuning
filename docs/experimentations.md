# Journal d'expérimentations

Documentation des runs d'entraînement et d'évaluation : ce qui a été lancé, avec
quels résultats, et ce qu'on en tire. C'est la matière brute pour la méthodologie
et les résultats du rapport final.

## Entraînement en local, suivi avec MLflow

**Statut** : résolu, 2026-09-21.

**Décision** : entraînement SFT et DPO sur la machine locale (GPU RTX 5060
Laptop, 8 Go de VRAM), pas de cloud pour cette partie. Suivi d'expérimentation
avec MLflow en local plutôt que W&B.

**Pourquoi** : GPU local suffisant, confirmé avec le mentor. MLflow déjà connu,
pas besoin d'un service hébergé pour un usage solo, et les courbes de loss
exportées suffisent pour le rapport et la soutenance (pas besoin du lien de
partage public de W&B).

**Point de vigilance** : 8 Go de VRAM est serré. À surveiller pendant le run
pilote : longueur de séquence, taille de batch, gradient checkpointing.

## Checkpoint SFT retenu : checkpoint-500, pas le checkpoint final

**Statut** : résolu, 2026-09-21.

**Le problème** : run complet SFT (`scripts/train_sft.py`, 750 steps, 3 epochs)
terminé sans erreur, loss stable et sans NaN. Mais en comparant `eval_loss`
step par step dans MLflow (expérience `triage-chsa-sft`, run `complet`) : la
loss de validation baisse jusqu'au step 500 (1,2875, son minimum), puis
stagne et remonte légèrement jusqu'à la fin (1,3076 au step 750). La loss
d'entraînement continue elle de baisser sur toute la durée (1,58 à 0,9 à 1,0).
Signe de sur apprentissage à partir de la 3e epoch.

**Décision** : garder `checkpoint-500` (le point de plus basse eval_loss)
comme modèle SFT de référence pour la suite (évaluation sur le split test,
puis point de départ du DPO), plutôt que `checkpoint_final` (fin
d'entraînement, step 750).

**Pourquoi ce choix** : le checkpoint avec la meilleure loss de validation
généralise mieux, c'est la définition même du critère qu'on cherche à
optimiser. Continuer avec le checkpoint final reviendrait à garder une
version qui a commencé à sur apprendre sans bénéfice réel.

**Ce qu'on perd avec ce choix** : rien d'identifié, sauvegarder plusieurs
checkpoints ne coûte que de l'espace disque, déjà fait par défaut
(`save_steps=50`).

**Comment vérifier plus tard** : à documenter dans le rapport comme exemple
concret de contrôle de sur apprentissage (le brief de mission insiste sur ce
point). Si une prochaine itération repart de zéro, envisager de réduire à 2
epochs plutôt que 3, ou d'ajouter un `early stopping` sur `eval_loss`.

## Run epochs2 : confirmation du choix de checkpoint-500, pas de changement

**Statut** : résolu, 2026-09-22.

**Le problème** : après avoir observé le sur apprentissage à partir du step
500 sur le run `complet` (voir plus bas), test ciblé pour vérifier
l'hypothèse : relancer un run dédié à 2 epochs (`--epochs 2 --nom-run
epochs2`, mêmes hyperparamètres et seed sinon) pour voir si un entraînement
prévu pour s'arrêter à 500 steps fait mieux que `checkpoint-500` extrait
d'un run prévu pour 750 steps.

**Ce qu'on a trouvé** : les deux courbes `eval_loss` sont quasiment
superposées step par step (ex. step 250 : 1,3022 vs 1,3042), ce qui confirme
la reproductibilité du pipeline. Au step 500, `checkpoint-500` du run
`complet` reste légèrement meilleur (1,2875) que la fin du run `epochs2`
(1,2930). Explication probable : le learning rate suit un schedule qui
décroît jusqu'à la fin prévue de l'entraînement. Dans `epochs2` (prévu pour
500 steps), le LR est déjà à zéro au step 500. Dans `complet` (prévu pour
750 steps), il reste encore un peu de marge à ce stade, d'où le léger
avantage.

**Décision** : garder `checkpoint-500` du run `complet` comme référence pour
le DPO, sans changement. Ce test confirme le choix plutôt qu'il ne le remet
en cause.

**Pourquoi ce choix** : la différence entre les deux (0,0055 en eval_loss)
est négligeable, et `checkpoint-500` du run `complet` est déjà légèrement
meilleur, pas de raison de changer.

**Ce qu'on garde de cette expérience** : un exemple concret de démarche
méthodique pour le rapport (observation du sur apprentissage, hypothèse,
test ciblé, confirmation), et une vérification indépendante de la
reproductibilité du pipeline (seed fixé, résultats cohérents d'un run à
l'autre).

## Génération SFT en boucle : problème de décodage, pas du modèle

**Statut** : résolu, 2026-09-21.

**Le problème** : première évaluation qualitative de `checkpoint-500` sur
`eval_clinique` (`scripts/evaluate_sft.py`) : le modèle boucle sur la même
phrase répétée 10 à 15 fois, sur quasiment tous les exemples générés en
`do_sample=False` sans pénalité.

**Ce qu'on a trouvé** : en ajoutant `repetition_penalty=1.3` et
`no_repeat_ngram_size=3` à la génération, le bouclage disparaît totalement.
Le texte généré devient cohérent en forme. C'est un artefact classique du
décodage greedy pur sur un modèle de base pas encore habitué à bien
s'arrêter, pas un signe que l'entraînement a échoué.

**Décision** : garder ces paramètres de génération pour toute évaluation
qualitative future (DPO inclus), et les reprendre au moment du déploiement
vLLM (étape 4) : sans ça, l'API produirait le même bouclage en démo.

**Ce qu'on perd avec ce choix** : rien identifié pour l'instant. À revalider
si le comportement diffère avec vLLM (moteur de génération différent de
`generate()` de Transformers).

**Comment vérifier plus tard** : reconfirmer que vLLM, au moment du
déploiement, applique une pénalité de répétition équivalente par défaut ou
via sa config.

## Qualité de fond du modèle SFT (avant DPO) : faux négatifs et hallucination

**Statut** : observé, 2026-09-21, à suivre.

**Le problème** : une fois le bouclage réglé (voir plus haut), 5
générations sur `eval_clinique` avec `checkpoint-500` montrent des problèmes
de fond, pas juste de forme :

- 2 cas sur 5 : mauvais diagnostic. Cas d'œdème pulmonaire sur surcharge
  rénale répondu "syndrome infectieux à pneumocystose". Cas de syndrome de
  Cushing répondu "Diabète insipide" (faux avant et après le changement de
  décodage, donc pas un artefact de génération). Ce sont des faux négatifs
  au sens large (mauvaise identification clinique), le risque que le mentor
  a désigné comme le plus problématique.
- 1 cas : médicament halluciné ("Lomégil®" à l'éphédrine pour les
  mamelons, qui n'existe pas).
- 1 cas : vocabulaire médical partiellement inventé dans une réponse par
  ailleurs structurée.

**Pourquoi ce n'est pas alarmant à ce stade** : c'est un modèle de 1,7
milliard de paramètres, entraîné en LoRA sur seulement 4000 exemples et 2
epochs utiles (voir la décision sur le sur apprentissage), sans alignement
DPO. Le DPO (étape 3 du plan) vise justement à renforcer la précision et la
sécurité des réponses. Ce n'est pas le modèle final.

**Ce qu'il faut faire avec ça** : garder ces 5 exemples (et le rapport
`docs/evaluation_sft.md`) comme référence "avant DPO", pour comparer avec les
mêmes cas après le DPO (prévu explicitement dans le plan d'action, étape 3).
Les garder aussi tels quels comme exemples concrets pour la section limites
et risques du rapport final, le mentor a insisté sur des exemples analysés
honnêtement plutôt que des métriques seules.

**Comment vérifier plus tard** : refaire tourner `scripts/evaluate_sft.py`
(ou son équivalent DPO) sur les mêmes exemples après le DPO, comparer
diagnostic par diagnostic.
