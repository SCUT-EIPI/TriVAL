# Dataset licenses and attribution

These terms apply to files under `benchmark/`. The root MIT license applies to the TriVAL implementation and runner; it does not relicense third-party benchmark data.

Upstream sources and notices were checked on 2026-10-14. The table describes the original benchmark sources. Local files are processed project snapshots; the exact upstream import revision and a complete record-level transformation history have not been reconstructed.

## License map

| Local data | Original benchmark source | Data terms |
|---|---|---|
| `NL4COP/*.json` | TriVAL authors; [TriVAL paper](https://arxiv.org/abs/2605.23966) | [CC BY 4.0](licenses/CC-BY-4.0.txt) |
| `IndustryOR.jsonl` | [ORLM](https://github.com/Cardinal-Operations/ORLM); [official data card](https://huggingface.co/datasets/CardinalOperations/IndustryOR) | [CC BY-NC 4.0](licenses/CC-BY-NC-4.0.txt), as stated in the dataset card |
| `Mamo_easy.jsonl`, `Mamo_complex.jsonl` | [Mamo](https://github.com/FreedomIntelligence/Mamo) | [CC BY-SA 4.0](licenses/Mamo-CC-BY-SA-4.0.txt) |
| `Optmath.jsonl` | [OptMATH](https://github.com/optsuite/OptMATH) | [Apache 2.0](licenses/Apache-2.0.txt), under the original repository license |
| `OptiBench.jsonl` | [OptiBench / ReSocratic](https://github.com/yangzhch6/PRIVATE-RS) | [Apache 2.0](licenses/Apache-2.0.txt), under the original repository license |
| `NL4Opt.jsonl` | [NL4Opt competition](https://github.com/nl4opt/nl4opt-competition) | [MIT](licenses/NL4Opt-MIT.txt), under the original code-and-dataset repository license |
| `NL4LP.jsonl` | [OptiMUS / NLP4LP](https://github.com/teshnizi/OptiMUS); [official dataset](https://huggingface.co/datasets/udell-lab/NLP4LP) | [CC BY-NC 4.0](licenses/CC-BY-NC-4.0.txt), with the upstream research-use notice |

The upstream [SIRL benchmark collection](https://github.com/Cardinal-Operations/SIRL/tree/main/test_data) also documents normalized and corrected versions of several benchmarks. Its public availability is not treated as a replacement for the original data terms.

The original license texts and dataset-specific notices govern use. Copies of common license texts are provided in `licenses/`.

## NL4COP

Copyright (c) 2026 Ziyang Fang, JinXi Wang, Jinghui Zhong, and Yew-Soon Ong.

The NL4COP data files, including problem descriptions, reference solutions, and reference solver code embedded in JSON, are licensed under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/). The full text is in [licenses/CC-BY-4.0.txt](licenses/CC-BY-4.0.txt).

When sharing or adapting NL4COP, credit the authors, link the license, cite the TriVAL paper, and indicate changes.

## Third-party notices

### IndustryOR

Original work: Chenyu Huang, Zhengyang Tang, Shixi Hu, Ruoqing Jiang, Xin Zheng, Dongdong Ge, Benyou Wang, and Zizhuo Wang. *ORLM: A Customizable Framework in Training Large Models for Automated Optimization Modeling*. Operations Research, 2025.

The [official IndustryOR data card](https://huggingface.co/datasets/CardinalOperations/IndustryOR/raw/main/README.md) states `cc-by-nc-4.0`. This data-specific notice is retained separately from the Apache 2.0 license for the ORLM repository. Credit the original authors, identify modifications, and follow the data license's non-commercial terms.

### Mamo

Original work: Xuhan Huang, Qingning Shen, Yan Hu, Anningzhe Gao, and Benyou Wang. *LLMs for Mathematical Modeling: Towards Bridging the Gap between Natural and Mathematical Languages*. Findings of NAACL, 2025.

The [original repository license](https://github.com/FreedomIntelligence/Mamo/blob/main/LICENSE) is CC BY-SA 4.0. Retain attribution and indicate modifications. Shared adaptations retain the applicable ShareAlike terms. The local easy and complex files are the project's processed optimization subsets.

### OptMATH

Original work: Hongliang Lu, Zhonglin Xie, Yaoyu Wu, Can Ren, Yuxuan Chen, and Zaiwen Wen. *OptMATH: A Scalable Bidirectional Data Synthesis Framework for Optimization Modeling*. ICML, 2025.

The [original repository license](https://github.com/optsuite/OptMATH/blob/main/LICENSE) is Apache 2.0. Preserve its license and notices, cite the original work, and identify changes to the local benchmark snapshot.

### OptiBench

Original work: Zhicheng Yang, Yiwei Wang, Yinya Huang, Zhijiang Guo, Wei Shi, Xiongwei Han, Liang Feng, Linqi Song, Xiaodan Liang, and Jing Tang. *OptiBench Meets ReSocratic: Measure and Improve LLMs for Optimization Modeling*. ICLR, 2025.

The [official code-and-data repository license](https://github.com/yangzhch6/PRIVATE-RS/blob/main/LICENSE) is Apache 2.0. Preserve its license and notices, cite the original work, and identify changes to the local snapshot.

### NL4Opt

Original work: Rindranirina Ramamonjison and coauthors. *NL4Opt Competition: Formulating Optimization Problems Based on Their Natural Language Descriptions*. NeurIPS 2022 Competition Track, PMLR, 2023.

The [original repository license](https://github.com/nl4opt/nl4opt-competition/blob/main/LICENSE) is MIT, copyright (c) 2022 Huawei Technologies. The full copyright and permission notice is retained in [licenses/NL4Opt-MIT.txt](licenses/NL4Opt-MIT.txt). The local file contains processed problem-and-answer records. The missing reference answer for local record ID `49` was filled as `"20.0"`; see the [correction notice](README.md#reference-answer-correction).

### NLP4LP / local NL4LP

Original work: Ali AhmadiTeshnizi, Wenzhi Gao, and Madeleine Udell. *OptiMUS: Scalable Optimization Modeling with (MI)LP Solvers and Large Language Models*. ICML, 2024.

The [OptiMUS README](https://github.com/teshnizi/OptiMUS#nlp4lp-dataset) and [dataset website](https://nlp4lp.vercel.app/) state CC BY-NC 4.0 for NLP4LP data and restrict it to research use. They also state that models trained using this dataset should not be used outside research purposes. Preserve that notice and follow the dataset-specific terms; the MIT license for OptiMUS code does not replace them.

### ComplexOR

Original work: Ziyang Xiao and coauthors. *Chain-of-Experts: When LLMs Meet Complex Operations Research Problems*. ICLR, 2024.

The checked upstream repository and README do not state a redistribution license. ComplexOR data is not included in this release. Obtain it from the [upstream repository](https://github.com/xzymustbexzy/Chain-of-Experts) subject to the original authors' terms; this repository grants no redistribution permission.

## Local processing notice

The local third-party snapshots use the fields documented in [README.md](README.md). Preparation included JSON/JSONL normalization, record selection, and corrections to some problem descriptions and reference answers. These are modified versions, not claims of unchanged upstream data.

Original authors retain their rights. Local processing does not replace original licenses or remove attribution requirements. See the [dataset version notice](README.md#dataset-version) for the released OptMath snapshot.

For NL4COP, the English [text normalization](README.md#text-normalization) corrects stray characters in two problem descriptions. Dataset IDs, instance values, reference solutions, and solver code are unchanged.

## License text sources

- CC BY 4.0: [SPDX license text](https://github.com/spdx/license-list-data/blob/main/text/CC-BY-4.0.txt).
- CC BY-NC 4.0: [SPDX license text](https://github.com/spdx/license-list-data/blob/main/text/CC-BY-NC-4.0.txt).
- Mamo CC BY-SA 4.0: copied from the original Mamo repository.
- Apache 2.0: copied from OptMATH; the official OptiBench repository has the same license text.
- NL4Opt MIT: copied from the original NL4Opt competition repository.
