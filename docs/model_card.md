---
license: apache-2.0
language:
- fr
- en
base_model: Qwen/Qwen3-1.7B-Base
datasets:
- rriviere/oc-llm-finetuning-dataset
tags:
- medical
- triage
- lora
- dpo
pipeline_tag: text-generation
---

# Agent de triage CHSA, Qwen3-1.7B

Modèle construit pour un POC d'agent de triage aux urgences (mission OpenClassrooms,
AI Engineer, pour le CHSA). Il lit la description d'un patient et renvoie un JSON avec
le niveau d'urgence, la spécialité, les symptômes, les signes d'alerte, une
justification et une recommandation.

C'est un prototype de recherche. **Il ne doit pas servir à trier de vrais patients.**

## Usage prévu

- Démontrer la faisabilité technique d'une aide au triage à l'accueil des urgences.
- Toujours avec un soignant qui garde la décision : le modèle propose, l'infirmier
  d'accueil décide.

Hors usage prévu : tout usage sur de vrais patients, tout usage sans supervision
humaine, tout usage comme avis médical.

## Format de sortie

```json
{
  "urgency_level": "maximum",
  "specialty": "cardiology",
  "key_symptoms": ["douleur thoracique constrictive", "sueurs"],
  "red_flags": ["tachycardie (pouls 110)"],
  "justification": "2 ou 3 phrases, dans la langue du cas.",
  "recommendation": "Une phrase courte, dans la langue du cas."
}
```

- `urgency_level` : `maximum`, `moderate` ou `deferred`.
- `specialty` : `cardiology`, `neurology`, `pulmonology`, `gastroenterology`,
  `trauma_orthopedics`, `obstetrics_gynecology`, `psychiatry`, `infectious_diseases`,
  `nephrology_urology` ou `general_medicine`.

## Utilisation

Le modèle a été entraîné avec une consigne précise. Il faut la reprendre telle quelle :
elle est construite par `construire_prompt("triage", cas)` dans `app/prompts.py` du
dépôt du projet. Le prompt finit par `Cas : <texte du patient>`, une ligne vide, puis
`Réponse :` et un retour à la ligne.

Décodage utilisé pour l'évaluation et l'API : glouton (`temperature=0`), sans pénalité
de répétition, `max_tokens=512`, arrêt au premier retour à la ligne (le JSON tient sur
une ligne). Une pénalité de fréquence abîme le JSON.

```python
from vllm import LLM, SamplingParams

from app.prompts import construire_prompt

llm = LLM("rriviere/triage-chsa-qwen3-1.7b", dtype="bfloat16", max_model_len=4096)
params = SamplingParams(temperature=0.0, max_tokens=512, stop=["\n"])
cas = "Homme de 62 ans, douleur thoracique constrictive depuis 40 minutes, sueurs."
print(llm.generate([construire_prompt("triage", cas)], params)[0].outputs[0].text)
```

## Entraînement

Modèle de base : [Qwen3-1.7B-Base](https://huggingface.co/Qwen/Qwen3-1.7B-Base).
Deux étapes, chacune avec un adaptateur LoRA, puis fusion des deux adaptateurs dans les
poids (le DPO part du modèle SFT fusionné).

Réglages communs : LoRA de rang 16, `lora_alpha` 32, dropout 0,05, sur `q_proj`,
`k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`. Longueur maximale
1024 tokens, bfloat16, seed 42.

| | SFT | DPO |
|---|---|---|
| Données | triage (JSON) et QA médicale, environ 5000 exemples | 5000 paires UltraMedical-Preference, tirées équilibrées sur la longueur |
| Epochs | 3 | 1 |
| Taux d'apprentissage | 2e-4 | 5e-5 |
| Batch effectif | 16 (2 x 8) | 16 (1 x 16) |
| Autre | | `beta` 0,3 |
| Checkpoint retenu | pas 600 (fin de la 2e epoch), meilleure loss de validation | pas 313 (fin du run) |
| Durée | 2 h 34 | 5 h 02 |

Matériel : une RTX 5060 Laptop (8 Go). Suivi des runs dans MLflow.

Les labels de triage ont été produits par Mistral Large en suivant un protocole écrit.
Les réponses des cas anglais ont été traduites pour que la justification suive la
langue du cas. Détails dans la dataset card de
[rriviere/oc-llm-finetuning-dataset](https://huggingface.co/datasets/rriviere/oc-llm-finetuning-dataset).

## Évaluation

Sur le split de test du dataset : 531 cas de triage (202 en français, 329 en anglais),
jamais vus à l'entraînement, découpés par cas pour éviter toute fuite. Les labels sont
ceux de Mistral Large. Une réponse invalide compte comme une erreur.

| Modèle | JSON valide | F1 macro | Rappel `maximum` | Sous triage | Sous triage grave | Sur triage |
|---|---|---|---|---|---|---|
| Toujours `maximum` (plancher) | 100 % | 0,21 | 1,00 | 0 % | 0 % | 53,3 % |
| Qwen3-1.7B-Base, 3 exemples | 70,2 % | 0,30 | 0,31 | 60,3 % | 61,3 % | 0,9 % |
| SFT | 100 % | 0,78 | 0,91 | 8,5 % | 0 % | 11,5 % |
| **SFT + DPO (ce modèle)** | 99,8 % | 0,77 | 0,94 | 7,2 % | 0 % | 13,2 % |

- Sous triage : patient classé moins urgent qu'il ne l'est.
- Sous triage grave : urgence vitale classée `deferred`.
- Sur triage : patient classé plus urgent qu'il ne l'est.

Résultats par langue pour ce modèle : F1 macro de 0,80 en français et 0,76 en anglais.
La justification est dans la langue du cas pour 99,8 % des réponses.

Seuils d'acceptation fixés avant l'évaluation : JSON valide ≥ 99 %, rappel sur
`maximum` ≥ 0,90, sous triage grave ≤ 1 %, sous triage ≤ 10 %, sur triage ≤ 25 %,
langue respectée ≥ 98 %. Le modèle les passe tous.

Marges d'erreur : avec 248 urgences vitales dans le test, le rappel sur `maximum` a un
intervalle à 95 % de 0,90 à 0,97. Aucun sous triage grave n'est observé, mais le vrai
taux peut aller jusqu'à environ 1,2 %.

## Limites et risques

**Labels non validés par des soignants.** Les niveaux d'urgence viennent de Mistral
Large, contrôlé à la main sur 30 à 50 cas par rapport au protocole, sans relecture
médicale. Les scores mesurent l'accord avec Mistral, pas une performance clinique.
Une partie des « erreurs » relues sur la validation sont des labels discutables.

**Hallucinations.** Le modèle peut inventer des mots ou des faits. Exemple observé :
« irradiation radiographeuse » au lieu de « irradiante ». La justification peut aussi
oublier un signe de gravité alors que le niveau est bon : une tension à 90/60 avec un
pouls à 110 absente des signes d'alerte.

**Urgences vitales ratées.** Environ 6 % des urgences vitales du test sont classées
`moderate`. Exemples vus sur la validation : une hématurie avec caillots sous
anticoagulant et une hémoglobine à 46 g/l, des syncopes à l'effort sur un
rétrécissement aortique serré.

**Biais de sources et de langue.** Les cas français viennent d'annales d'examens
médicaux (MediQAl), les cas anglais de vignettes de QCM (UltraMedical). Ce sont des
cas écrits par des médecins, pas des descriptions de patients. Le modèle n'a pas été
évalué sur le langage d'un vrai patient. Le DPO est entièrement en anglais.

**Mélange des classes.** Près de la moitié des cas de test sont des urgences vitales,
bien plus que dans une vraie salle d'urgences. La précision sur `maximum` serait plus
basse en conditions réelles.

**Petit modèle.** 1,7 milliard de paramètres : connaissances médicales limitées,
raisonnement court.

## Conformité

Un système de triage des patients aux urgences est une IA à haut risque selon l'AI
Act. Ce modèle est un POC et ne remplit pas les exigences d'une mise en production :
validation clinique des labels par des urgentistes, évaluation sur des données réelles,
hébergement certifié HDS en Europe pour des données de santé.

Aucune donnée de patient réel n'a servi à l'entraînement : les sources sont publiques
et ont été anonymisées.
