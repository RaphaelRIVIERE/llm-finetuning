---
license:
- cc-by-4.0
- apache-2.0
- mit
language:
- fr
- en
tags:
- medical
- healthcare
- triage
- clinical
task_categories:
- text-generation
pretty_name: Dataset médical bilingue, triage CHSA
configs:
- config_name: sft
  data_files:
  - split: train
    path: sft/train.jsonl
  - split: validation
    path: sft/validation.jsonl
  - split: test
    path: sft/test.jsonl
- config_name: dpo
  data_files:
  - split: train
    path: dpo/train.jsonl
  - split: validation
    path: dpo/validation.jsonl
  - split: test
    path: dpo/test.jsonl
---

# Dataset médical bilingue, triage CHSA

Dataset construit pour un POC d'agent de triage médical aux urgences (mission
OpenClassrooms, AI Engineer, pour le CHSA). Il sert à fine tuner un petit modèle
(Qwen3-1.7B-Base) en deux temps : un SFT, puis un alignement DPO.

Deux configurations :

- `sft` : des exemples instruction / réponse, pour deux tâches.
  - **triage** : un cas de patient, et la réponse attendue en JSON (niveau d'urgence,
    spécialité, symptômes, signes d'alerte, justification, recommandation) ;
  - **qa** : une question médicale, et la réponse attendue en texte libre.
- `dpo` : des paires de préférences (un prompt, une réponse préférée, une réponse
  écartée), toutes en anglais.

Le code qui produit ce dataset est dans le dépôt
[RaphaelRIVIERE/llm-finetuning](https://github.com/RaphaelRIVIERE/llm-finetuning)
(`scripts/extraction.py`, `scripts/examples.py`, notebooks 01 à 05).

**Ce dataset ne contient aucune donnée de vrai patient du CHSA.** Les cas viennent de
datasets publics : cas d'examens de médecine, QCM, fiches d'information, questions
générées. Les labels de triage ont été produits par un LLM et n'ont pas été validés par
un soignant (voir Limites).

## Composition

**SFT** : 6315 exemples.

| Tâche | Source | Langue | train | validation | test |
| --- | --- | --- | --- | --- | --- |
| triage | MediQAl | fr | 1615 | 202 | 202 |
| triage | UltraMedical-Preference | en | 2637 | 330 | 329 |
| qa | MediQAl | fr | 331 | 34 | 51 |
| qa | FrenchMedMCQA | fr | 66 | 13 | 5 |
| qa | MedQuAD | en | 401 | 49 | 50 |
| **total** | | | **5050** | **628** | **637** |

Niveaux d'urgence des 5315 exemples de triage :

| Langue | maximum | moderate | deferred |
| --- | --- | --- | --- |
| fr | 1001 | 670 | 348 |
| en | 1479 | 1021 | 796 |

Les cas viennent d'examens de médecine, qui choisissent volontiers des situations
graves : `maximum` y est bien plus fréquent qu'aux urgences réelles.

**DPO** : 79 015 paires (63 148 train, 7927 validation, 7940 test).

## Schéma

Champs communs aux deux configurations :

| Champ | Type | Description |
| --- | --- | --- |
| `id` | string | Identifiant unique de l'exemple |
| `langue` | string | `fr` ou `en` |
| `source` | string | `mediqal`, `frenchmedmcqa`, `medquad` ou `ultramedical_preference` |
| `licence_source` | string | Licence du dataset d'origine (voir Sources) |
| `split` | string | `train`, `validation` ou `test` |
| `niveau_confiance` | string | `haut` ou `moyen`, fiabilité de la source (voir plus bas) |
| `transformations` | liste | Traitements appliqués à l'exemple (voir plus bas) |
| `cle_cas` | string | Clé du cas, qui sert au découpage et au contrôle de fuite |
| `tache` | string | `triage` ou `qa` : dit quelle consigne ajouter devant le texte |

Champs de `sft` :

| Champ | Type | Description |
| --- | --- | --- |
| `instruction` | string | Le cas de patient (triage) ou la question (qa), sans consigne |
| `reponse` | string | La réponse attendue : un JSON pour le triage, du texte pour le QA |
| `urgency_level` | string | Niveau attendu (`maximum`, `moderate`, `deferred`), vide pour le QA |
| `symptomes` | liste | Symptômes extraits du cas (triage), vide pour le QA |
| `antecedents` | liste | Antécédents écrits dans le cas (triage), vide sinon |
| `constantes_vitales` | objet | FC, PA, FR, SpO2, température quand le cas les donne (triage) |
| `annotateur` | string | Modèle qui a produit le label de triage, vide pour le QA |
| `version_prompt` | string | Version de la consigne d'annotation, vide pour le QA |

Champs de `dpo` :

| Champ | Type | Description |
| --- | --- | --- |
| `prompt` | string | La question posée, sans consigne |
| `chosen` | string | Réponse préférée |
| `rejected` | string | Réponse écartée |
| `type_paire` | string | Comment la source a construit la paire : `hard`, `length`, `easy`, `human` |
| `score_chosen` | nombre | Note sur 5 de la réponse préférée, donnée par la source |
| `score_rejected` | nombre | Note sur 5 de la réponse écartée |

Valeurs de `transformations` : `anonymisation_noms` (nom de patient remplacé par
`[PATIENT]`), `retrait_choix_qcm` (choix du QCM retirés d'une vignette),
`reformulation_qcm_vers_qa` (QCM FrenchMedMCQA mis en question / réponse),
`correction_ponctuation` (« ? ? » final de MedQuAD corrigé), `annotation_triage`
(label produit par le LLM annotateur), `traduction_anglais` (champs texte du label
traduits), `split_reassigne` (split différent de celui de la source).

### La réponse de triage

Le champ `reponse` d'un exemple de triage est un JSON, toujours avec ces clés dans cet
ordre :

```json
{"urgency_level": "maximum", "specialty": "general_medicine", "key_symptoms": ["brûlure oculaire", "exposition à l'eau de javel"], "red_flags": ["exposition chimique oculaire"], "justification": "Une exposition à un produit chimique corrosif comme l'eau de javel dans l'œil constitue une urgence ophtalmologique immédiate. Le risque de lésions irréversibles de la cornée ou de perte de vision justifie une prise en charge sans délai.", "recommendation": "Rincer immédiatement l'œil à l'eau ou au sérum physiologique et orienter vers un ophtalmologiste en urgence."}
```

- `urgency_level` : `maximum` (danger vital ou risque de séquelle, à voir tout de
  suite), `moderate` (problème aigu, à voir dans les heures qui viennent), `deferred`
  (rien d'urgent). Ce sont les trois niveaux de la mission, repris des niveaux 1 et 2,
  3, puis 4 et 5 de l'échelle de tri FRENCH.
- `specialty` : une valeur parmi `cardiology`, `neurology`, `pulmonology`,
  `gastroenterology`, `trauma_orthopedics`, `obstetrics_gynecology`, `psychiatry`,
  `infectious_diseases`, `nephrology_urology`, `general_medicine` (valeur par défaut
  quand aucune ne convient).
- `justification` et `recommendation` sont écrites dans la langue du cas.

### La consigne

Le dataset ne contient pas de consigne : `instruction` et `prompt` sont le texte seul.
La consigne est ajoutée à l'entraînement, à l'évaluation et dans l'API par une même
fonction (`construire_prompt`, `app/prompts.py`), selon `tache`. Les paires DPO prennent
la consigne de QA.

## Labels de triage

Aucune des sources n'a de niveau d'urgence. Les labels ont été produits par un LLM, en
suivant un protocole écrit pour ce projet
([docs/protocole_triage.md](https://github.com/RaphaelRIVIERE/llm-finetuning/blob/main/docs/protocole_triage.md)) :
trois niveaux, sept règles (dans le doute, prendre le niveau le plus urgent ; juger le
patient tel qu'il arrive ; la gravité d'une maladie n'est pas l'urgence...) et six
exemples.

- **Annotateur** : Mistral Large (`mistral-large-2512`), `temperature` à 0, seed fixée.
  Le schéma JSON de la réponse est imposé au décodage, donc les niveaux et les
  spécialités ne peuvent pas sortir des listes. 5319 cas annotés, tous valides, avec
  une seule version de consigne (`version_prompt`).
- **Métadonnées** : en même temps que le label, l'annotateur extrait les antécédents et
  les constantes vitales écrits dans le cas, et laisse le champ vide quand le cas n'en
  parle pas. Seules les constantes chiffrées sont gardées.
- **Traduction** : pour les cas anglais, l'annotateur avait écrit la justification et
  la recommandation en français. Ces champs, avec `key_symptoms` et `red_flags`, ont été
  traduits en anglais par le même modèle, sans lui envoyer ni le cas, ni le niveau, ni
  la spécialité : les labels n'ont pas pu changer (`traduction_anglais`).
- **Écartés** : 4 vignettes anglaises de moins de 100 caractères, trop pauvres pour
  être triées (« A neonate presented to OPD with following features »).
- **Relecture** : le split `test` du triage (531 cas) doit être relu à la main pour
  servir de vérité terrain. Cette relecture n'est pas encore faite : pour l'instant, le
  test contient les labels de Mistral.

## Découpage par cas

Le découpage est fait une seule fois, sur toutes les sources ensemble, avant de
construire les exemples. L'unité est le **cas**, pas l'exemple :

- MediQAl : le cas clinique (plusieurs questions portent sur le même patient), ou la
  question s'il n'y en a pas ;
- MedQuAD et FrenchMedMCQA : la question ;
- UltraMedical-Preference : le prompt.

La clé de cas (`cle_cas`) est faite des 100 premiers caractères du texte normalisé, et
anonymisé pour les sources françaises. Elle regroupe aussi les suites de cas (le même
patient, avec un paragraphe de plus) et les prompts UltraMedical recopiés de MedQuAD.

Toutes les clés sont réparties en train (80 %), validation (10 %) et test (10 %), avec
un tirage stratifié par source et, pour les cas de triage, par niveau d'urgence. Les
splits d'origine des sources ne sont pas repris (`split_reassigne`).

Contrôle de fuite, sur les exemples SFT et les paires DPO réunis : aucune clé de cas
n'est dans deux splits. Un même cas peut donner un exemple de triage, des questions de
QA et des paires DPO : ils sont toujours dans le même split.

## Construction

**SFT, triage.** Les cas sont les cas cliniques de MediQAl (trois configurations) et les
vignettes cliniques d'UltraMedical-Preference qui décrivent un patient qui arrive avec
un problème, repérés par des règles écrites à la main. Les choix du QCM sont retirés
des vignettes, ils soufflaient le diagnostic à l'annotateur. Un seul cas est gardé par
clé, le plus court (l'arrivée du patient). Tous les cas français sont annotés, et 3300
vignettes anglaises tirées au hasard.

**SFT, QA.** Questions de MediQAl (configuration `oeq`), FrenchMedMCQA et MedQuAD :
49 doublons exacts retirés, « ? ? » final de 322 questions MedQuAD corrigé. Les QCM
FrenchMedMCQA gardent leurs cinq propositions dans l'instruction, et la réponse est la
lettre avec son texte : pour une question négative (« laquelle est fausse ? »), le
modèle apprend à désigner la bonne proposition, pas une affirmation fausse. 1000
exemples sont tirés, autant en français qu'en anglais, en gardant les proportions des
splits. Le QA garde au modèle des connaissances générales et la réponse en texte
libre, le triage reste la tâche principale.

**DPO.** UltraMedical-Preference, sans les triples (prompt, chosen, rejected) en
double (10 646 retirés). Les paires où la réponse préférée n'a pas un score strictement
meilleur que la réponse écartée sont écartées (5765 paires, dont 5187 de type
`length`) : la préférence n'y reposait sur rien de mesuré.

**Biais de longueur.** La réponse préférée est la plus longue dans 65 % des paires.
Le biais vient des paires `hard` (80 %) et `easy` (89 %). Les paires `length` vont dans
l'autre sens (33 %) : elles ont été construites pour montrer qu'une réponse plus longue
n'est pas forcément meilleure, et sont donc gardées. Le dataset ne corrige pas ce biais.
Il peut l'être au moment de tirer les paires d'entraînement, avec autant de paires où
la réponse préférée est la plus longue que de paires où elle est la plus courte.

## Sources et licences

| Source | Dépôt utilisé | Licence | Usage | Citation |
| --- | --- | --- | --- | --- |
| MediQAl | [ANR-MALADES/MediQAl](https://huggingface.co/datasets/ANR-MALADES/MediQAl) | CC-BY-4.0 | triage et QA (fr) | Bazoge, *MediQAl*, Scientific Data, 2026 |
| FrenchMedMCQA | [nthngdy/frenchmedmcqa](https://huggingface.co/datasets/nthngdy/frenchmedmcqa) | Apache 2.0 | QA (fr) | Labrak et al., *FrenchMedMCQA*, LOUHI 2022 (arXiv:2304.04280) |
| MedQuAD | [keivalya/MedQuad-MedicalQnADataset](https://huggingface.co/datasets/keivalya/MedQuad-MedicalQnADataset) | CC-BY-4.0 | QA (en) | Ben Abacha et Demner-Fushman, BMC Bioinformatics, 2019 |
| UltraMedical-Preference | [TsinghuaC3I/UltraMedical-Preference](https://huggingface.co/datasets/TsinghuaC3I/UltraMedical-Preference) | MIT | triage (en) et DPO | Zhang et al., *UltraMedical*, 2024 (arXiv:2406.03949) |

Les dépôts de FrenchMedMCQA et MedQuAD utilisés sont des miroirs sans licence
affichée. Leurs licences viennent des versions d'origine :
[qanastek/frenchmedmcqa](https://huggingface.co/datasets/qanastek/frenchmedmcqa)
(Apache 2.0) et [abachaa/MedQuAD](https://github.com/abachaa/MedQuAD) (CC-BY-4.0). Les
versions exactes des quatre sources sont fixées par leur commit Hugging Face.

## Anonymisation et RGPD

Les quatre sources sont publiques. Les patients des cas d'examen sont fictifs.

- **MediQAl et FrenchMedMCQA** : les noms de patients suivent les conventions des cas
  d'examen (titre + initiale, prénom + initiale, prénom + âge). Des règles les
  remplacent par `[PATIENT]` (`anonymisation_noms`, 726 exemples), puis un texte où un
  motif trouve encore un nom est supprimé.
- **UltraMedical-Preference** : les questions de forum (ChatDoctor,
  Medical-Instruct-120k) contiennent de vrais noms, emails et téléphones de patients.
  Elles sont écartées, pas anonymisées : leurs auteurs n'ont pas consenti à cet usage.
  Les paires où un nom est repéré sont aussi supprimées.
- **MedQuAD** : les seuls contacts sont ceux d'organismes de santé publics, gardés.
- Il n'existe pas de table de correspondance entre `[PATIENT]` et un nom d'origine :
  c'est une anonymisation, pas une pseudonymisation.
- **Envoi à Mistral pour l'annotation** : seuls des cas déjà anonymisés ou filtrés ont
  été envoyés. Mistral AI est une entreprise française, et l'usage des données envoyées
  pour entraîner ses modèles a été désactivé sur le compte avant le premier envoi.

## Niveau de confiance

`niveau_confiance` décrit la fiabilité de la **source**, pas la confiance de
l'annotateur dans son label de triage.

- **haut** : contenu d'origine humaine, validé, licence claire. `mediqal` (cas
  cliniques rédigés par des professionnels) et `frenchmedmcqa` (questions réelles
  d'examen, correction indiquée par les auteurs).
- **moyen** : source fiable mais assemblée ou annotée de façon largement automatique.
  `medquad` (fiches d'organismes de santé publics, agrégées automatiquement) et
  `ultramedical_preference` (préférences notées par GPT-4, revues par des experts mais
  pas exemple par exemple).

## Limites

- **Les labels de triage viennent d'un LLM**, guidé par un protocole écrit par
  quelqu'un qui n'est pas soignant et qui n'a pas été validé médicalement. Seule la
  relecture du test, quand elle sera faite, servira de vérité terrain, et elle non plus
  n'est pas faite par un soignant.
- **Des cas d'examen, pas des patients.** Les cas sont écrits par des enseignants en
  médecine, dans un style très différent de ce qu'un patient raconte à l'accueil des
  urgences. Ils contiennent parfois des résultats d'examens qu'on n'a pas encore à
  l'arrivée.
- **Les niveaux ne suivent pas la répartition des urgences réelles** : près de la
  moitié des cas sont `maximum`.
- **`specialty` est grossière** : dix valeurs, et `general_medicine` regroupe tout ce
  qui n'y entre pas (ophtalmologie, endocrinologie, dermatologie...).
- **Anonymisation par règles** : 74 textes MediQAl gardent un prénom seul (« Kévin
  présente... »). Ce sont des patients fictifs.
- **Le DPO est seulement en anglais**, aucune source de paires de préférences en
  français n'a été trouvée. Rien ne garantit que l'alignement profite autant au
  français.
- **Champs extraits partiels** : `antecedents` et `constantes_vitales` ne sont remplis
  que pour les cas de triage, et seulement quand le cas les donne (constantes
  présentes dans 1707 cas sur 5315).

## Citations

```
@article{bazoge2026mediqal,
  title={MediQAl: A French Medical Question Answering Dataset for Knowledge and Reasoning Evaluation},
  author={Bazoge, Adrien},
  journal={Scientific Data},
  year={2026},
  publisher={Nature Publishing Group UK London}
}

@inproceedings{labrak-etal-2022-frenchmedmcqa,
    title = "{F}rench{M}ed{MCQA}: A {F}rench Multiple-Choice Question Answering Dataset for Medical domain",
    author = "Labrak, Yanis and Bazoge, Adrien and Dufour, Richard and Daille, Beatrice and
      Gourraud, Pierre-Antoine and Morin, Emmanuel and Rouvier, Mickael",
    booktitle = "Proceedings of the 13th International Workshop on Health Text Mining and Information Analysis (LOUHI)",
    year = "2022",
    address = "Abu Dhabi, United Arab Emirates (Hybrid)",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2022.louhi-1.5",
    pages = "41--46",
}

@ARTICLE{BenAbacha-BMC-2019,
  author  = {Asma {Ben Abacha} and Dina Demner{-}Fushman},
  title   = {A Question-Entailment Approach to Question Answering},
  journal = {{BMC} Bioinform.},
  volume  = {20},
  number  = {1},
  pages   = {511:1--511:23},
  year    = {2019},
  url     = {https://bmcbioinformatics.biomedcentral.com/articles/10.1186/s12859-019-3119-4}
}

@misc{zhang2024ultramedical,
      title={UltraMedical: Building Specialized Generalists in Biomedicine},
      author={Kaiyan Zhang and Sihang Zeng and Ermo Hua and Ning Ding and Zhang-Ren Chen and
        Zhiyuan Ma and Haoxin Li and Ganqu Cui and Biqing Qi and Xuekai Zhu and Xingtai Lv and
        Hu Jinfang and Zhiyuan Liu and Bowen Zhou},
      year={2024},
      eprint={2406.03949},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```
