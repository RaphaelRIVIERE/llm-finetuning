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
dataset_info:
- config_name: dpo
  features:
  - name: id
    dtype: string
  - name: langue
    dtype: string
  - name: source
    dtype: string
  - name: licence_source
    dtype: string
  - name: split
    dtype: string
  - name: niveau_confiance
    dtype: string
  - name: transformations
    sequence: string
  - name: prompt
    dtype: string
  - name: chosen
    dtype: string
  - name: rejected
    dtype: string
  - name: cle_cas
    dtype: string
  - name: type_paire
    dtype: string
  - name: score_chosen
    dtype: float64
  - name: score_rejected
    dtype: float64
  - name: tache
    dtype: string
---

# Dataset médical bilingue, triage CHSA

Ce dataset sert à fine tuner Qwen3-1.7B-Base pour un POC d'agent de triage aux urgences
(mission OpenClassrooms, AI Engineer, pour le CHSA). Il a deux configurations :

- `sft` : des exemples instruction / réponse. Soit un cas de patient avec le triage
  attendu en JSON (tâche `triage`), soit une question médicale avec sa réponse en texte
  (tâche `qa`).
- `dpo` : des paires de préférences en anglais (une question, une bonne réponse, une
  moins bonne).

**Il n'y a aucune donnée de vrai patient.** Tout vient de datasets publics (cas
d'examens de médecine, QCM, fiches d'information). Les labels de triage ont été produits
par un LLM et n'ont pas été validés par un soignant.

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

Sur les 5315 cas de triage, 2480 sont `maximum`, 1691 `moderate` et 1144 `deferred`.

**DPO** : 79 015 paires (63 148 train, 7927 validation, 7940 test).

## Schéma

Champs présents dans les deux configurations :

| Champ | Description |
| --- | --- |
| `id` | Identifiant de l'exemple |
| `langue` | `fr` ou `en` |
| `source` | `mediqal`, `frenchmedmcqa`, `medquad` ou `ultramedical_preference` |
| `licence_source` | Licence du dataset d'origine |
| `split` | `train`, `validation` ou `test` |
| `niveau_confiance` | `haut` ou `moyen`, fiabilité de la source |
| `transformations` | Liste des traitements appliqués à l'exemple |
| `cle_cas` | Clé du cas, utilisée pour le découpage |
| `tache` | `triage` ou `qa` |

Champs de `sft` :

| Champ | Description |
| --- | --- |
| `instruction` | Le cas de patient ou la question |
| `reponse` | La réponse attendue : un JSON pour le triage, du texte pour le QA |
| `urgency_level` | `maximum`, `moderate` ou `deferred` (vide pour le QA) |
| `symptomes` | Symptômes du cas (triage seulement) |
| `antecedents` | Antécédents écrits dans le cas (triage seulement) |
| `constantes_vitales` | FC, PA, FR, SpO2, température quand le cas les donne |
| `annotateur` | Modèle qui a produit le label de triage |
| `version_prompt` | Version de la consigne d'annotation |

Champs de `dpo` :

| Champ | Description |
| --- | --- |
| `prompt` | La question |
| `chosen` | La réponse préférée |
| `rejected` | La réponse écartée |
| `type_paire` | Type de paire donné par la source : `hard`, `length`, `easy`, `human` |
| `score_chosen`, `score_rejected` | Notes sur 5 données par la source |

Valeurs possibles de `transformations` :

- `anonymisation_noms` : nom du patient remplacé par `[PATIENT]`
- `retrait_choix_qcm` : choix du QCM retirés du cas
- `reformulation_qcm_vers_qa` : QCM transformé en question / réponse
- `correction_ponctuation` : ponctuation corrigée
- `annotation_triage` : label produit par le LLM
- `traduction_anglais` : label traduit en anglais
- `split_reassigne` : split différent de celui de la source

### La réponse de triage

Pour le triage, `reponse` est un JSON avec toujours les mêmes clés :

```json
{"urgency_level": "maximum", "specialty": "general_medicine", "key_symptoms": ["brûlure oculaire", "exposition à l'eau de javel"], "red_flags": ["exposition chimique oculaire"], "justification": "Une exposition à un produit chimique corrosif comme l'eau de javel dans l'œil constitue une urgence ophtalmologique immédiate. Le risque de lésions irréversibles de la cornée ou de perte de vision justifie une prise en charge sans délai.", "recommendation": "Rincer immédiatement l'œil à l'eau ou au sérum physiologique et orienter vers un ophtalmologiste en urgence."}
```

Les trois niveaux d'urgence :

- `maximum` : danger vital ou risque de séquelle, à voir tout de suite ;
- `moderate` : problème aigu, à voir dans les heures qui viennent ;
- `deferred` : rien d'urgent.

`specialty` prend une valeur parmi dix spécialités, avec `general_medicine` quand aucune
ne convient. `justification` et `recommendation` sont écrites dans la langue du cas.

## Construction

1. **Choix des cas de triage.** Les cas cliniques de MediQAl (fr) et les vignettes
   d'UltraMedical-Preference (en) qui décrivent un patient qui arrive avec un problème.
   Les choix du QCM sont retirés, car ils donnaient le diagnostic.
2. **Annotation.** Aucune source n'a de niveau d'urgence. Mistral Large les a produits
   en suivant un protocole écrit pour le projet : les trois niveaux, quelques règles
   (dans le doute, prendre le niveau le plus urgent ; juger le patient tel qu'il
   arrive) et six exemples. `temperature` à 0 et schéma JSON imposé. Il extrait aussi les antécédents et
   les constantes vitales.
3. **Traduction.** Pour les cas anglais, les textes du label ont été traduits en anglais
   par le même modèle, sans lui montrer le niveau ni la spécialité.
4. **QA.** Des questions de MediQAl, FrenchMedMCQA et MedQuAD, sans les doublons. Le QA
   aide le modèle à garder ses connaissances générales.
5. **DPO.** Les paires d'UltraMedical-Preference, sans les doublons ni les paires où la
   réponse préférée n'a pas une meilleure note.
6. **Découpage.** Tout est découpé en une fois en train (80 %), validation (10 %) et
   test (10 %). L'unité est le cas, pas l'exemple : un même patient ne se retrouve
   jamais dans deux splits, ce qui évite les fuites entre entraînement et test.

## Sources et licences

| Source | Dépôt utilisé | Licence | Usage | Citation |
| --- | --- | --- | --- | --- |
| MediQAl | [ANR-MALADES/MediQAl](https://huggingface.co/datasets/ANR-MALADES/MediQAl) | CC-BY-4.0 | triage et QA (fr) | Bazoge, *MediQAl*, Scientific Data, 2026 |
| FrenchMedMCQA | [nthngdy/frenchmedmcqa](https://huggingface.co/datasets/nthngdy/frenchmedmcqa) | Apache 2.0 | QA (fr) | Labrak et al., *FrenchMedMCQA*, LOUHI 2022 (arXiv:2304.04280) |
| MedQuAD | [keivalya/MedQuad-MedicalQnADataset](https://huggingface.co/datasets/keivalya/MedQuad-MedicalQnADataset) | CC-BY-4.0 | QA (en) | Ben Abacha et Demner-Fushman, BMC Bioinformatics, 2019 |
| UltraMedical-Preference | [TsinghuaC3I/UltraMedical-Preference](https://huggingface.co/datasets/TsinghuaC3I/UltraMedical-Preference) | MIT | triage (en) et DPO | Zhang et al., *UltraMedical*, 2024 (arXiv:2406.03949) |

Les dépôts FrenchMedMCQA et MedQuAD utilisés sont des copies sans licence affichée. Leur
licence est celle des versions d'origine
([qanastek/frenchmedmcqa](https://huggingface.co/datasets/qanastek/frenchmedmcqa) et
[abachaa/MedQuAD](https://github.com/abachaa/MedQuAD)).

## Anonymisation et RGPD

- Les quatre sources sont publiques et les patients des cas d'examen sont fictifs.
- Dans les sources françaises, les noms de patients sont remplacés par `[PATIENT]`. Il
  n'existe pas de table pour retrouver le nom d'origine.
- Les questions de forum d'UltraMedical contiennent de vrais noms, emails et
  téléphones. Elles sont retirées du dataset.
- Seuls des cas déjà anonymisés ont été envoyés à Mistral pour l'annotation, avec
  l'option d'entraînement sur nos données désactivée.

## Niveau de confiance

`niveau_confiance` dit si la **source** est fiable. Il ne dit rien sur la qualité du
label de triage.

- **haut** : contenu écrit et validé par des humains (`mediqal`, `frenchmedmcqa`).
- **moyen** : source fiable mais assemblée ou notée surtout de façon automatique
  (`medquad`, `ultramedical_preference`).

## Limites

- **Les labels de triage viennent d'un LLM** et n'ont pas été relus par un soignant,
  même dans le `test`. Un score sur ce dataset mesure l'accord avec Mistral, pas une
  performance clinique.
- **Des cas d'examen, pas de vrais patients.** Le style est loin de ce qu'un patient
  raconte à l'accueil, et les cas graves sont surreprésentés.
- **`specialty` est grossière** : `general_medicine` regroupe tout ce qui ne rentre pas
  dans les neuf autres.
- **Le DPO est seulement en anglais.** Rien ne garantit que l'alignement profite autant
  au français.
- **Biais de longueur dans le DPO** : la réponse préférée est la plus longue dans 65 %
  des paires.

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
