# Sources de données : origine et licence

| Source                     | Lien Hugging Face | Licence | Usage | Note |
| --------------------------- | ------------------ | ------- | ----- | ---- |
| MediQAl                    | [ANR-MALADES/MediQAl](https://huggingface.co/datasets/ANR-MALADES/MediQAl) | CC-BY-4.0 | SFT (français) | Attribution obligatoire, citer le papier associé (Bazoge, MediQAl, Scientific Data, 2026). |
| FrenchMedMCQA               | [nthngdy/frenchmedmcqa](https://huggingface.co/datasets/nthngdy/frenchmedmcqa) | Apache 2.0 (confirmée via la source d'origine) | SFT (français) | Le dépôt utilisé (nthngdy) est un miroir non officiel, sans licence affichée. La version canonique, publiée par Yanis Labrak (un des auteurs du papier) sous [qanastek/frenchmedmcqa](https://huggingface.co/datasets/qanastek/frenchmedmcqa) et sur [GitHub](https://github.com/qanastek/FrenchMedMCQA), indique Apache 2.0 dans sa section Licensing Information et dans ses métadonnées. Citer Labrak et al., FrenchMedMCQA, LOUHI 2022 (arXiv:2304.04280). |
| MedQuAD                    | [keivalya/MedQuad-MedicalQnADataset](https://huggingface.co/datasets/keivalya/MedQuad-MedicalQnADataset) | CC-BY-4.0 (via la source originale) | SFT (anglais) | Ce dépôt HF est un miroir sans licence affichée. La source originale ([abachaa/MedQuAD](https://github.com/abachaa/MedQuAD)) est sous CC-BY-4.0, confirmée dans son `readme.txt`. Citer Ben Abacha et Demner-Fushman, BMC Bioinformatics, 2019. |
| UltraMedical-Preference     | [TsinghuaC3I/UltraMedical-Preference](https://huggingface.co/datasets/TsinghuaC3I/UltraMedical-Preference) | MIT | DPO (anglais) | Citation recommandée (Zhang et al., UltraMedical, 2024, arXiv:2406.03949), non obligatoire sous MIT. |

## Citations complètes

Récupérées directement sur la fiche Hugging Face ou le dépôt GitHub de chaque
source d'origine (pas le miroir), à reprendre telles quelles dans la fiche du
dataset final.

**MediQAl**

```
@article{bazoge2026mediqal,
  title={MediQAl: A French Medical Question Answering Dataset for Knowledge and Reasoning Evaluation},
  author={Bazoge, Adrien},
  journal={Scientific Data},
  year={2026},
  publisher={Nature Publishing Group UK London}
}
```

**FrenchMedMCQA**

```
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
```

**MedQuAD**

```
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
```

**UltraMedical-Preference**

```
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
