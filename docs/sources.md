# Sources de données : origine et licence

| Source                     | Lien Hugging Face | Licence | Usage | Note |
| --------------------------- | ------------------ | ------- | ----- | ---- |
| MediQAl                    | [ANR-MALADES/MediQAl](https://huggingface.co/datasets/ANR-MALADES/MediQAl) | CC-BY-4.0 | SFT (français) | Attribution obligatoire, citer le papier associé (Bazoge et al., MediQAl, Scientific Data). Date de publication à confirmer. |
| FrenchMedMCQA               | [nthngdy/frenchmedmcqa](https://huggingface.co/datasets/nthngdy/frenchmedmcqa) | Apache 2.0 (confirmée via la source d'origine) | SFT (français) | Le dépôt utilisé (nthngdy) est un miroir non officiel, sans licence affichée. La version canonique, publiée par Yanis Labrak (un des auteurs du papier) sous [qanastek/frenchmedmcqa](https://huggingface.co/datasets/qanastek/frenchmedmcqa) et sur [GitHub](https://github.com/qanastek/FrenchMedMCQA), indique Apache 2.0 dans sa section Licensing Information et dans ses métadonnées. Citer Labrak et al., FrenchMedMCQA, LOUHI 2022 (arXiv:2304.04280). |
| MedQuAD                    | [keivalya/MedQuad-MedicalQnADataset](https://huggingface.co/datasets/keivalya/MedQuad-MedicalQnADataset) | CC-BY-4.0 (via la source originale) | SFT (anglais) | Ce dépôt HF est un miroir sans licence affichée. La source originale ([abachaa/MedQuAD](https://github.com/abachaa/MedQuAD)) est sous CC-BY-4.0. Citer Ben Abacha et Demner-Fushman, BMC Bioinformatics, 2019. |
| UltraMedical-Preference     | [TsinghuaC3I/UltraMedical-Preference](https://huggingface.co/datasets/TsinghuaC3I/UltraMedical-Preference) | MIT | DPO (anglais) | Citation recommandée (Zhang et al., UltraMedical, 2024), non obligatoire sous MIT. |

## À faire avant de publier le dataset final

- Confirmer la référence exacte du papier MediQAl (l'année trouvée en ligne
  semble incohérente, à vérifier directement sur la page du dataset ou l'article).
- Inclure les citations demandées dans la fiche du dataset final publié sur
  Hugging Face.
