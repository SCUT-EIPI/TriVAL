# Dataset licenses and attribution

| Local data | Original benchmark source | Data terms |
|---|---|---|
| `NL4COP/*.json` | TriVAL authors; [TriVAL paper](https://arxiv.org/abs/2605.23966) | [CC BY 4.0](licenses/CC-BY-4.0.txt) |
| `IndustryOR.jsonl` | [ORLM](https://github.com/Cardinal-Operations/ORLM); [official data card](https://huggingface.co/datasets/CardinalOperations/IndustryOR) | [CC BY-NC 4.0](licenses/CC-BY-NC-4.0.txt), as stated in the dataset card |
| `Mamo_easy.jsonl`, `Mamo_complex.jsonl` | [Mamo](https://github.com/FreedomIntelligence/Mamo) | [CC BY-SA 4.0](licenses/Mamo-CC-BY-SA-4.0.txt) |
| `Optmath.jsonl` | [OptMATH](https://github.com/optsuite/OptMATH) | [Apache 2.0](licenses/Apache-2.0.txt), under the original repository license |
| `OptiBench.jsonl` | [OptiBench / ReSocratic](https://github.com/yangzhch6/PRIVATE-RS) | [Apache 2.0](licenses/Apache-2.0.txt), under the original repository license |
| `NL4Opt.jsonl` | [NL4Opt competition](https://github.com/nl4opt/nl4opt-competition) | [MIT](licenses/NL4Opt-MIT.txt), under the original code-and-dataset repository license |
| `NL4LP.jsonl` | [OptiMUS / NLP4LP](https://github.com/teshnizi/OptiMUS); [official dataset](https://huggingface.co/datasets/udell-lab/NLP4LP) | [CC BY-NC 4.0](licenses/CC-BY-NC-4.0.txt), with the upstream research-use notice |

## NL4COP

Copyright (c) 2026 Ziyang Fang, JinXi Wang, Jinghui Zhong, and Yew-Soon Ong.

The NL4COP data files, including problem descriptions, reference solutions, and reference solver code embedded in JSON, are licensed under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/). The full text is in [licenses/CC-BY-4.0.txt](licenses/CC-BY-4.0.txt).

Please cite the [TriVAL paper](https://arxiv.org/abs/2605.23966) when using NL4COP.

## Third-party attribution

- **IndustryOR** — Chenyu Huang, Zhengyang Tang, Shixi Hu, Ruoqing Jiang, Xin Zheng, Dongdong Ge, Benyou Wang, and Zizhuo Wang. *ORLM: A Customizable Framework in Training Large Models for Automated Optimization Modeling*. Operations Research, 2025.
- **Mamo** — Xuhan Huang, Qingning Shen, Yan Hu, Anningzhe Gao, and Benyou Wang. *LLMs for Mathematical Modeling: Towards Bridging the Gap between Natural and Mathematical Languages*. Findings of NAACL, 2025.
- **OptMATH** — Hongliang Lu, Zhonglin Xie, Yaoyu Wu, Can Ren, Yuxuan Chen, and Zaiwen Wen. *OptMATH: A Scalable Bidirectional Data Synthesis Framework for Optimization Modeling*. ICML, 2025.
- **OptiBench** — Zhicheng Yang, Yiwei Wang, Yinya Huang, Zhijiang Guo, Wei Shi, Xiongwei Han, Liang Feng, Linqi Song, Xiaodan Liang, and Jing Tang. *OptiBench Meets ReSocratic: Measure and Improve LLMs for Optimization Modeling*. ICLR, 2025.
- **NL4Opt** — Rindranirina Ramamonjison and coauthors. *NL4Opt Competition: Formulating Optimization Problems Based on Their Natural Language Descriptions*. NeurIPS 2022 Competition Track, PMLR, 2023.
- **NLP4LP** — Ali AhmadiTeshnizi, Wenzhi Gao, and Madeleine Udell. *OptiMUS: Scalable Optimization Modeling with (MI)LP Solvers and Large Language Models*. ICML, 2024.

The [NLP4LP dataset notice](https://nlp4lp.vercel.app/) restricts the data to research use and specifies that models trained on it should only be used for research. The NL4Opt data retains the [Huawei copyright and MIT permission notice](licenses/NL4Opt-MIT.txt).

## Changes to the released data

The released third-party data includes record selection, JSONL conversion, and corrections to descriptions and answers. The [SIRL benchmark collection](https://github.com/Cardinal-Operations/SIRL/tree/main/test_data) also documents normalized versions.

- **OptMath.** The released subset excludes IDs `67` and `76`. The 129-record version reported in the paper included ID `67`.
- **NL4Opt.** The missing reference answer for record `49` was filled with `"20.0"`.
- **NL4COP.** Two descriptions received text corrections: the volume unit in `mkp_001` and the wording in `travelling_salesman_problem_001`.
