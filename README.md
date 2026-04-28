# TriVAL

Official repository for the paper:

> **TriVAL: A Tri-Validation Framework for Faithful Automatic Optimization Modeling**

TriVAL is a tri-validation framework for faithful automatic optimization modeling from natural-language problem descriptions. It validates three key modeling stages: semantic specification, mathematical formulation, and solver code generation. At each stage, TriVAL follows a construct-validate-revise loop to identify and correct errors before they propagate through the modeling pipeline.

This repository will host the official implementation, benchmark resources, and reproduction scripts for the paper. The full source code will be released here.

> Note: The dependency file, environment example, and source code will be added with the official code release.

---

## Quick Start

### Environment & Installation

Recommended environment:

- Python 3.13+
- `uv` package manager

Clone repository:

```bash
git clone https://github.com/SCUT-ELOG/TriVAL.git
cd TriVAL
```

Create the virtual environment and install dependencies:

```bash
uv sync
```

Configure API keys:

```bash
cp .env.example .env
```

Open `.env` and set the key for the provider you intend to use:

```dotenv
DEEPSEEK_API_KEY=sk-...
OPENAI_API_KEY=sk-...
```

---

## Run Example

Use `run.py` at the project root. All runs are launched via `uv run`:

```bash
uv run python run.py --provider <provider> --model <model> (--dataset <name> --index <n> | --file <path>)
```

### Arguments

| Argument | Required | Description |
|---|---|---|
| `--provider` | Yes | LLM provider, such as `deepseek` or `openai` |
| `--model` | Yes | Model name, such as `deepseek-reasoner` or `gpt-5.1` |
| `--dataset` | Yes, or `--file` | Dataset name |
| `--index` | With `--dataset` | 0-based record index in the dataset |
| `--file` | Yes, or `--dataset` | Path to a `.txt` file used as problem input |

Run on a dataset record:

```bash
uv run python run.py --provider deepseek --model deepseek-reasoner --dataset [dataset_name] --index 0
```

Run on a custom problem from a text file:

```bash
uv run python run.py --provider openai --model gpt-5.1 --file /path/to/problem.txt
```

The entire content of the `.txt` file is used as the problem description.

---

## Citation

If you use TriVAL in your research or academic publications, please cite this project as follows:

```bibtex
@software{TriVAL,
  author = {Ziyang Fang and Jinxi Wang and Jinghui Zhong and Yew-Soon Ong},
  title = {TriVAL: A Tri-Validation Framework for Faithful Automatic Optimization Modeling},
  year = {2026},
  url = {https://github.com/SCUT-ELOG/TriVAL},
  version = {1.0}
}
```