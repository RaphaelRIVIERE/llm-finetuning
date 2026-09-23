# Journal d'expérimentations

Documentation des runs d'entraînement et d'évaluation : ce qui a été lancé, avec
quels résultats, et ce qu'on en tire. C'est la matière brute pour la méthodologie
et les résultats du rapport final.

## Sommaire

| Section | Statut | Décision en bref |
|---|---|---|
| [Entraînement en local, suivi avec MLflow](#entraînement-en-local-suivi-avec-mlflow) | Résolu, 2026-09-21 | GPU local (RTX 5060, 8 Go) et suivi MLflow local, pas de cloud. |
| [Checkpoint SFT retenu : checkpoint-500, pas le checkpoint final](#checkpoint-sft-retenu--checkpoint-500-pas-le-checkpoint-final) | Résolu, 2026-09-21 | checkpoint-500 gardé comme référence, meilleure eval_loss avant sur apprentissage. |
| [Génération SFT en boucle : problème de décodage, pas du modèle](#génération-sft-en-boucle--problème-de-décodage-pas-du-modèle) | Résolu, 2026-09-21 | repetition_penalty=1.3 et no_repeat_ngram_size=3 règlent le bouclage. |
| [Qualité de fond du modèle SFT (avant DPO) : faux négatifs et hallucination](#qualité-de-fond-du-modèle-sft-avant-dpo--faux-négatifs-et-hallucination) | Observé, 2026-09-21, à suivre | Faux négatifs et hallucinations relevés, gardés comme référence avant DPO. |
| [Run epochs2 : confirmation du choix de checkpoint-500, pas de changement](#run-epochs2--confirmation-du-choix-de-checkpoint-500-pas-de-changement) | Résolu, 2026-09-22 | Run dédié à 2 epochs confirme checkpoint-500 du run complet. |
| [Checkpoint DPO retenu : checkpoint-250, pas le checkpoint final](#checkpoint-dpo-retenu--checkpoint-250-pas-le-checkpoint-final) | Résolu, 2026-09-22 | checkpoint-250 gardé comme référence DPO, même logique que pour le SFT. |
| [Comparaison avant / après DPO sur eval_clinique : pas d'amélioration claire](#comparaison-avant--après-dpo-sur-eval_clinique--pas-damélioration-claire) | Observé, 2026-09-22, limite documentée du POC | Pas d'amélioration nette, régressions repérées (code switching, hallucinations). |
| [Modèle retenu pour la démo : SFT + DPO malgré l'absence d'amélioration claire](#modèle-retenu-pour-la-démo--sft--dpo-malgré-labsence-damélioration-claire) | Résolu, 2026-09-22 | SFT + DPO (checkpoint-250) gardé pour la démo, malgré l'absence de gain net. |
| [Décodage vLLM : frequency_penalty à la place de repetition_penalty](#décodage-vllm--frequency_penalty-à-la-place-de-repetition_penalty) | Résolu, 2026-09-23 | frequency_penalty=0.5 et max_tokens=512 retenus pour l'API. |
| [Questions libres : forte sensibilité à la formulation](#questions-libres--forte-sensibilité-à-la-formulation) | Observé, 2026-09-23, limite documentée du POC | Réponses incohérentes entre deux formulations d'un même cas sur 4 cas sur 5, le décodage n'y change rien. |

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

**Suite, 2026-09-23** : vLLM n'a pas d'équivalent à `no_repeat_ngram_size`, et
`repetition_penalty=1.3` seul abîme le texte. Remplacé par
`frequency_penalty=0.5` dans l'API, voir la section « Décodage vLLM » plus bas.

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

## Run epochs2 : confirmation du choix de checkpoint-500, pas de changement

**Statut** : résolu, 2026-09-22.

**Le problème** : après avoir observé le sur apprentissage à partir du step
500 sur le run `complet` (voir plus haut), test ciblé pour vérifier
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

## Checkpoint DPO retenu : checkpoint-250, pas le checkpoint final

**Statut** : résolu, 2026-09-22.

**Le problème** : run complet DPO (`scripts/train_dpo.py`, 313 steps, 1 epoch
sur 5000 paires sous échantillonnées, à partir de `checkpoint-500` du SFT
fusionné) terminé sans erreur. `eval_loss` baisse jusqu'au step 250 (0,3830,
minimum), puis remonte légèrement (0,4008 au step 300, 0,4031 au step final
313). Même schéma de léger sur apprentissage en toute fin d'entraînement que
pour le SFT.

**Ce qu'on observe côté métriques DPO** : `rewards/accuracies` (fréquence à
laquelle le modèle préfère la réponse chosen) passe de 69% en début
d'entraînement à un plateau autour de 76 à 82% dans la seconde moitié.
`rewards/margins` (écart de score entre chosen et rejected) grimpe de 0,5 à
un plateau autour de 1,4 à 1,9. Le modèle apprend bien à séparer les deux
réponses dans le bon sens.

**Décision** : garder `checkpoint-250` (meilleure eval_loss) comme modèle
DPO de référence, pas `checkpoint_final` (step 313), même raisonnement que
pour `checkpoint-500` du SFT.

**Comment vérifier plus tard** : évaluer `checkpoint-250` sur `eval_clinique`
et comparer aux générations `checkpoint-500` (avant DPO) déjà documentées
dans `docs/evaluation_sft.md`, en particulier sur les faux négatifs et
l'hallucination de médicament déjà repérés.

## Comparaison avant / après DPO sur eval_clinique : pas d'amélioration claire

**Statut** : observé, 2026-09-22, à traiter comme limite documentée du POC.

**Le problème** : `scripts/evaluate_dpo.py` génère les mêmes 5 exemples
français (déjà dans `docs/evaluation_sft.md`) et 5 exemples anglais, avec
`checkpoint-500` (SFT seul) et `checkpoint-250` (SFT + DPO), mêmes
paramètres de décodage. Rapport dans `docs/evaluation_dpo.md`.

**Ce qu'on trouve** :

- Le faux négatif le plus critique (cas de syndrome de Cushing, exemple 4)
  n'est pas corrigé : réponse identique avant et après, "Diabète insipide",
  toujours faux.
- Un signe de dégradation du français malgré `beta=0.3` : sur l'exemple 1,
  la réponse après DPO part en français puis bascule en plein milieu sur du
  texte anglais, alors que rien dans la question ne le justifie.
- Pas d'amélioration claire de la justesse ailleurs, et des hallucinations
  nouvelles ou plus marquées après DPO : un volume de lait maternel de
  "cinq litres" par jour inventé (exemple 3), un terme médical inventé
  ("syndrome diabétique butyrique", exemple 5), une statistique de
  prévalence non vérifiable ("1 sur un million", exemple 8). Deux réponses
  anglaises (exemples 7 et 10) dégénèrent en texte tronqué et peu lisible en
  fin de génération après DPO. Nuance ajoutée le 2026-09-23 : le même
  phénomène (mots collés sans espace) apparaît déjà avant DPO sur ces deux
  mêmes exemples, et les tests de décodage vLLM montrent qu'il vient surtout de
  `repetition_penalty=1.3`. Il disparaît avec `frequency_penalty=0.5` (voir
  la section « Décodage vLLM »). Ce point n'est donc pas à mettre sur le
  compte du DPO seul.

**Hypothèse probable** : les métriques d'entraînement (`rewards/accuracies`
en hausse, `eval_loss` en baisse, voir plus haut) montrent que le modèle
apprend à distinguer chosen de rejected sur le dataset d'entraînement, mais
UltraMedical-Preference tend à préférer des réponses plus longues et
détaillées, pas nécessairement plus justes cliniquement. Le modèle semble
avoir en partie appris à être plus disert, pas plus exact ou plus sûr. Mode
d'échec connu du DPO/RLHF (optimiser la forme préférée par les annotateurs
plutôt que le fond).

**Remarque technique en passant** : le texte "avant DPO" généré par ce
script diffère légèrement de celui déjà documenté dans
`docs/evaluation_sft.md` pour les mêmes exemples et les mêmes paramètres de
génération (`do_sample=False`). Léger défaut de déterminisme du décodage
greedy sur GPU avec certains noyaux d'attention (comportement connu, pas
propre à ce projet). Les deux versions restent comparables qualitativement
(mêmes types d'erreurs), mais ce n'est pas une reproductibilité bit à bit.

**Ce qu'il faut faire avec ça** : documenter honnêtement dans le rapport
final comme limite du POC, avec ces exemples concrets plutôt que de
présenter seulement les métriques d'entraînement qui, prises seules,
suggéraient une amélioration. Ne pas relancer un DPO différent sans
hypothèse plus solide sur ce qui manque (plus de données ne corrige pas
forcément un problème de justesse factuelle sur un modèle de 1,7 milliard
de paramètres). Garder pour la roadmap de passage à l'échelle : DPO sur un
modèle plus grand, paires de préférence construites spécifiquement pour la
justesse clinique plutôt que reprises telles quelles d'un dataset généraliste.

## Modèle retenu pour la démo : SFT + DPO malgré l'absence d'amélioration claire

**Statut** : résolu, 2026-09-22.

**Le problème** : la comparaison avant/après DPO (voir plus haut) ne montre
pas d'amélioration claire, et quelques régressions (code switching, deux
hallucinations plus marquées). Question à trancher : déployer le modèle SFT
+ DPO tel quel pour la démo (étape 4), ou revenir au SFT seul
(`checkpoint-500`) ?

**Décision** : garder SFT + DPO (`checkpoint-250`) pour la démo.

**Pourquoi ce choix** : la mission demande explicitement de suivre la
méthodologie SFT puis DPO (`docs/contexte.md`), et la grille d'évaluation
valorise une analyse critique honnête des résultats plutôt qu'un résultat
parfait. Documenter un DPO qui n'apporte pas le bénéfice espéré, avec des
exemples concrets à l'appui, est une démonstration de rigueur méthodologique
en soi.

**Comment vérifier plus tard** : si le temps le permet, reprendre le DPO
comme axe d'amélioration pour la roadmap de passage à l'échelle (paires de
préférence construites spécifiquement pour la justesse clinique, modèle
plus grand), plutôt que de retenter un DPO similaire sur ce POC.

## Décodage vLLM : frequency_penalty à la place de repetition_penalty

**Statut** : résolu, 2026-09-23.

**Le problème** : l'API reprenait `repetition_penalty=1.3` des évaluations
Transformers, mais pas `no_repeat_ngram_size=3`, qui n'existe pas dans
`SamplingParams` de vLLM. Les premiers tests manuels de l'API donnaient des
réponses très courtes, avec des termes inventés et des mélanges de langue.

**Ce qu'on a testé** : `scripts/test_decodage.py` génère les 10 exemples de
`evaluate_dpo.py` (5 FR, 5 EN) avec le modèle final, en greedy, sous
plusieurs réglages. Le rapport note aussi le nombre de tokens et la raison
de l'arrêt (`stop` ou `length`).

- Passage 1 (`docs/test_decodage_vllm.md`, max_tokens=256) :
  `repetition_penalty` à 1.3, 1.1 et 1.0, `frequency_penalty=0.5`, et un
  mélange `repetition_penalty=1.1` + `presence_penalty=0.3`.
- Passage 2 (`docs/test_decodage_vllm_2.md`, max_tokens=512) :
  `frequency_penalty` à 0.3, 0.5 et 0.7.

**Ce qu'on a trouvé** :

- `repetition_penalty=1.3` abîme le texte : mots collés sans espace sur les
  réponses anglaises longues (exemples 7 et 10), mots déformés en français
  (« allattement », « Hypoglicidmie »). Une pénalité aussi forte finit par
  pénaliser les espaces et les mots courants.
- Sans pénalité, le bouclage du SFT revient sur 3 exemples français sur 5.
- `repetition_penalty=1.1`, avec ou sans `presence_penalty`, est plus
  lisible mais invente encore des termes (« ventriculonévrose »,
  « hydropnée »).
- `frequency_penalty=0.3` laisse encore une boucle sur l'exemple 1. À 0.7,
  le modèle évite les mots utiles à répéter (« infarctus » devient
  « myopatie ») et invente davantage.
- `frequency_penalty=0.5` donne les réponses les plus propres, sans boucle,
  et les mêmes sorties d'un passage à l'autre.
- Les réponses courtes ne sont pas coupées : presque toutes s'arrêtent sur
  `stop`, c'est le modèle qui s'arrête de lui même, en ligne avec les
  réponses courtes de MediQAl. Seul l'exemple 10 atteignait 256 tokens, il
  se termine seul à 350 tokens avec la limite à 512.
- Le cas de Cushing (« Diabète insipide ») et l'exemple 8 donnent la même
  réponse sous tous les réglages : ces erreurs viennent du modèle, pas du
  décodage.

**Décision** : `frequency_penalty=0.5`, sans `repetition_penalty`, et
`max_tokens=512` dans `app/main.py`.

**Ce qu'on perd avec ce choix** : l'API ne décode plus exactement comme les
évaluations Transformers (`docs/evaluation_sft.md`, `docs/evaluation_dpo.md`),
qui gardent `repetition_penalty=1.3` et `no_repeat_ngram_size=3`. Les
réponses de l'API ne sont donc pas comparables mot pour mot avec ces
rapports. Le réglage ne corrige pas non plus le fond : les erreurs de
diagnostic et certaines hallucinations restent (exemple 6 : hyperuricémie
et orotate inventés).

**Comment vérifier plus tard** : 10 exemples, c'est peu. Refaire un contrôle
sur un plus grand échantillon d'`eval_clinique` au moment de l'évaluation
clinique finale, avec ces paramètres.

## Questions libres : forte sensibilité à la formulation

**Statut** : observé, 2026-09-23, limite documentée du POC.

**Le problème** : premiers appels manuels à l'API avec le nouveau décodage
(`frequency_penalty=0.5`), sur une question libre, pas au format « Cas
clinique / Question » de l'entraînement. Deux formulations qui ne diffèrent
que par le début de la phrase :

- « J'ai 35 ans avec des douleur en bas du dos, douleur a l'épaule et au
  genoux. Quel diagnostic peut être envisagé au vu des signes cliniques et
  biologiques ? » Réponse : « Syndrome de la lombalgie cervicale » répété 5
  fois. La boucle revient malgré `frequency_penalty`, et le terme n'a pas de
  sens (lombalgie pour le bas du dos, cervical pour le cou).
- « Homme de 35 ans avec des douleur en bas du dos, douleur a l'épaule et au
  genoux. [même question] » Réponse : « Syndrome de l'os intervertébral »,
  puis « Syndrome de l'os intervertebral avec syndrome de la rotule », puis
  « ... avec syndrome de la fémur ». Plus de boucle franche, mais des
  diagnostics inventés, et une répétition seulement masquée (le mot perd son
  accent pour échapper à la pénalité).

**Ce qu'on en tire** :

- Le modèle est très sensible à la formulation. La tournure à la troisième
  personne, plus proche des cas cliniques de MediQAl, suffit à changer la
  forme de la réponse. Or un agent de triage recevra surtout des messages
  libres, écrits comme le premier.
- Le décodage règle la forme, pas le fond. Dans les deux cas, la piste
  classique pour un homme jeune avec des douleurs du bas du dos et de
  plusieurs articulations (spondylarthrite) n'apparaît pas. Même famille
  d'erreur que le cas de Cushing.
- `frequency_penalty=0.5` ne suffit pas toujours à empêcher la répétition
  quand le modèle est très sûr de lui.

**Ce qu'on fait** : passage 3 de `scripts/test_decodage.py`
(`docs/test_decodage_vllm_3.md`). 5 cas posés chacun sous deux formes
(première personne comme un patient, troisième personne comme un cas
clinique) : le cas ci dessus, une douleur thoracique évocatrice d'infarctus,
une céphalée brutale évocatrice d'hémorragie méningée, une méningite (en
anglais), et un rhume banal comme témoin de sur estimation de la gravité.
Trois réglages comparés : `frequency_penalty=0.5` seul, plus
`repetition_penalty=1.1`, ou plus `presence_penalty=0.5`. Pas de réponse
attendue : on juge la forme et la cohérence, pas la justesse médicale, qui
demande une référence validée par un clinicien.

**Ce qu'on a trouvé** :

- Plus aucune boucle, sous les trois réglages.
- Le réglage compte peu. En formulation cas clinique, les trois donnent
  exactement la même réponse (un seul mot). `repetition_penalty=1.1` ajoute
  de la dérive (« syndrome d'entropion » pour des douleurs articulaires,
  « crise cardiaque » pour un mal de tête). `presence_penalty=0.5` donne
  presque toujours la même chose que `frequency_penalty=0.5` seul. On garde
  donc `frequency_penalty=0.5` seul dans l'API.
- Les deux formulations d'un même cas donnent des réponses différentes sur
  4 cas sur 5. Douleur thoracique : « crise aiguë de myocardique » côté
  patient, « Pneumothorax » côté cas clinique. Céphalée brutale : « mal de
  crâne » contre « Trombophlébite aortique ». Rhume : « infection
  respiratoire aiguë » contre « Gingivostomatite ». Seule la méningite, en
  anglais, est cohérente entre les deux formes. Quand deux réponses se
  contredisent, au moins l'une des deux est fausse, sans avoir besoin d'un
  avis médical pour le dire.
- Mots déformés ou inventés : « myocardique » employé comme un nom,
  « Trombophlébite », « Syndrome de l'os intervertébral ».
- Non déterminisme : la question « J'ai 35 ans... » envoyée seule à l'API
  donnait « lombalgie cervicale » répété 5 fois, la même question générée en
  lot de 10 par le script donne une liste différente, avec le même réglage.
  Explication probable : les calculs GPU changent légèrement selon la
  composition du lot, et le greedy peut prendre une autre route. En
  production, une même question peut donc donner deux réponses différentes
  selon la charge du serveur.

**Comment vérifier plus tard** : à garder quoi qu'il arrive pour la section
limites du rapport, avec les deux formulations côte à côte. Piste pour la
roadmap : ajouter au dataset SFT des questions formulées comme un patient,
pas seulement des cas d'examen.
