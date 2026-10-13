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

`urgency_level` vaut `maximum`, `moderate` ou `deferred`. `specialty` prend une valeur
parmi dix spécialités, avec `general_medicine` quand aucune ne convient.

## Utilisation

Le modèle a été entraîné avec cette consigne exacte. Il faut la reprendre telle quelle,
sinon les réponses se dégradent.

```python
from vllm import LLM, SamplingParams

CONSIGNE = """Tu fais le triage d'un patient à l'accueil des urgences. Réponds uniquement avec un objet JSON qui a ces clés, dans cet ordre :
- "urgency_level" : maximum, moderate ou deferred
- "specialty" : cardiology, neurology, pulmonology, gastroenterology, trauma_orthopedics, obstetrics_gynecology, psychiatry, infectious_diseases, nephrology_urology ou general_medicine
- "key_symptoms" : liste de chaînes courtes
- "red_flags" : liste de chaînes courtes, vide s'il n'y en a pas
- "justification" : 2 ou 3 phrases, dans la langue du cas
- "recommendation" : une phrase courte, dans la langue du cas"""

cas = "Homme de 62 ans, douleur thoracique constrictive depuis 40 minutes, sueurs."
prompt = f"{CONSIGNE}\n\nCas : {cas}\n\nRéponse :\n"

llm = LLM("rriviere/triage-chsa-qwen3-1.7b", dtype="bfloat16", max_model_len=4096)
params = SamplingParams(temperature=0.0, max_tokens=512, stop=["\n"])
print(llm.generate([prompt], params)[0].outputs[0].text)
```

Les réglages de génération comptent :

- `temperature=0.0` : le modèle prend toujours le mot le plus probable, donc le même
  cas donne toujours la même réponse ;
- `stop=["\n"]` : le JSON tient sur une ligne, la génération s'arrête à la fin de cette
  ligne ;
- pas de pénalité de fréquence : elle pousse le modèle à éviter les guillemets et les
  virgules qu'il vient d'écrire, et casse le JSON.

## Entraînement

Modèle de base : [Qwen3-1.7B-Base](https://huggingface.co/Qwen/Qwen3-1.7B-Base). Un
SFT puis un DPO, chacun avec LoRA : seuls de petits poids ajoutés sont entraînés, le
modèle de base reste gelé. Après chaque étape, ces poids sont ajoutés au modèle, le DPO
repart donc du modèle SFT. Le modèle publié est un modèle complet, qui se charge sans
adaptateur.

LoRA de rang 16 (`lora_alpha` 32, dropout 0,05) sur toutes les couches d'attention et
du MLP. Longueur maximale 1024 tokens, bfloat16.

| | SFT | DPO |
|---|---|---|
| Données | environ 5000 exemples de triage et de QA médicale | 5000 paires UltraMedical-Preference |
| Epochs | 3 | 1 |
| Taux d'apprentissage | 2e-4 | 5e-5 (`beta` 0,3) |
| Batch effectif | 16 | 16 |
| Checkpoint retenu | pas 600, meilleure loss de validation | fin du run |

Entraîné sur une RTX 5060 Laptop (8 Go). Le détail des données est sur la page du dataset
[rriviere/oc-llm-finetuning-dataset](https://huggingface.co/datasets/rriviere/oc-llm-finetuning-dataset).

## Évaluation

Sur le split de test du dataset : 531 cas de triage (202 en français, 329 en anglais),
jamais vus à l'entraînement. Les labels sont ceux de Mistral Large. Une réponse
invalide compte comme une erreur.

| Modèle | JSON valide | F1 macro | Rappel `maximum` | Sous triage | Sous triage grave | Sur triage |
|---|---|---|---|---|---|---|
| Toujours `maximum` (plancher) | 100 % | 0,21 | 1,00 | 0 % | 0 % | 53,3 % |
| Qwen3-1.7B-Base, 3 exemples | 70,2 % | 0,30 | 0,31 | 60,3 % | 61,3 % | 0,9 % |
| SFT | 100 % | 0,78 | 0,91 | 8,5 % | 0 % | 11,5 % |
| **SFT + DPO (ce modèle)** | 99,8 % | 0,77 | 0,94 | 7,2 % | 0 % | 13,2 % |

- Sous triage : patient classé moins urgent qu'il ne l'est.
- Sous triage grave : urgence vitale classée `deferred`.
- Sur triage : patient classé plus urgent qu'il ne l'est.

La justification est écrite dans la langue du cas pour 99,8 % des réponses.

Le modèle passe tous les seuils d'acceptation fixés avant l'évaluation. Avec 248
urgences vitales dans le test, son rappel sur `maximum` est entre 0,90 et 0,97 (à
95 %).

## Limites et risques

- **Labels non validés par des soignants.** Les niveaux d'urgence viennent de Mistral
  Large, sans relecture médicale. Les scores mesurent l'accord avec Mistral, pas une
  performance clinique.
- **Hallucinations.** Le modèle peut inventer des mots ou oublier un signe de gravité
  dans sa justification, par exemple une tension basse absente des signes d'alerte.
- **Urgences vitales ratées.** Environ 6 % des urgences vitales du test sont classées
  `moderate`.
- **Biais de sources et de langue.** Les cas sont écrits par des médecins pour des
  examens, pas par des patients. Le DPO est entièrement en anglais.
- **Mélange des classes.** Près de la moitié des cas de test sont des urgences vitales,
  bien plus qu'aux vraies urgences.
- **Petit modèle.** 1,7 milliard de paramètres : connaissances médicales limitées,
  raisonnement court.

## Conformité

Un système de triage des patients aux urgences est une IA à haut risque selon l'AI
Act. Ce modèle est un POC et ne remplit pas les exigences d'une mise en production :
validation clinique des labels par des urgentistes, évaluation sur des données réelles,
hébergement certifié HDS en Europe pour des données de santé.

Aucune donnée de patient réel n'a servi à l'entraînement : les sources sont publiques
et ont été anonymisées.
