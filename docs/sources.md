# Sources de données : origine et licence

| Source                     | Lien Hugging Face | Licence | Usage | Note |
| --------------------------- | ------------------ | ------- | ----- | ---- |
| MediQAl                    | [ANR-MALADES/MediQAl](https://huggingface.co/datasets/ANR-MALADES/MediQAl) | CC-BY-4.0 | SFT (français) | Attribution obligatoire, citer le papier associé (Bazoge et al., MediQAl, Scientific Data). Date de publication à confirmer. |
| FrenchMedMCQA               | [nthngdy/frenchmedmcqa](https://huggingface.co/datasets/nthngdy/frenchmedmcqa) | Non spécifiée | SFT (français) | Aucun champ licence sur la page HF, README vide. À clarifier avant publication du dataset final : vérifier le dépôt d'origine ou contacter l'auteur. |
| MedQuAD                    | [keivalya/MedQuad-MedicalQnADataset](https://huggingface.co/datasets/keivalya/MedQuad-MedicalQnADataset) | CC-BY-4.0 (via la source originale) | SFT (anglais) | Ce dépôt HF est un miroir sans licence affichée. La source originale ([abachaa/MedQuAD](https://github.com/abachaa/MedQuAD)) est sous CC-BY-4.0. Citer Ben Abacha et Demner-Fushman, BMC Bioinformatics, 2019. |
| UltraMedical-Preference     | [TsinghuaC3I/UltraMedical-Preference](https://huggingface.co/datasets/TsinghuaC3I/UltraMedical-Preference) | MIT | DPO (anglais) | Citation recommandée (Zhang et al., UltraMedical, 2024), non obligatoire sous MIT. |

## À faire avant de publier le dataset final

- Clarifier la licence de FrenchMedMCQA. Sans réponse claire, décider si on
  garde cette source ou si on la retire du dataset final.
- Confirmer la référence exacte du papier MediQAl (l'année trouvée en ligne
  semble incohérente, à vérifier directement sur la page du dataset ou l'article).
- Inclure les citations demandées dans la fiche du dataset final publié sur
  Hugging Face.
