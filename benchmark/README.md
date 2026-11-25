# Benchmark datasets

[NL4COP](NL4COP/) contains 150 instances across 50 combinatorial optimization problem types. Each type has a simple, medium, and hard instance. The JSON files include the problem description, a reference solution, and reference Python solver code.

## Available datasets

| Dataset option | Path | Records |
|---|---|---:|
| `nl4cop` | `NL4COP/*.json` | 150 |
| `industryor` | `IndustryOR.jsonl` | 99 |
| `mamo_complex` | `Mamo_complex.jsonl` | 210 |
| `mamo_easy` | `Mamo_easy.jsonl` | 642 |
| `optmath` | `Optmath.jsonl` | 128 |
| `optibench` | `OptiBench.jsonl` | 403 |
| `nl4opt` | `NL4Opt.jsonl` | 205 |
| `nl4lp` | `NL4LP.jsonl` | 178 |

Use the dataset option with `run.py --dataset`. See the [quick start](../README.md#quick-start) for a complete example.

## Record fields

| Dataset | ID | Problem input | Reference answer | Metadata |
|---|---|---|---|---|
| NL4COP | `problem_id` | `problem_description` | `reference_solution` | `problem_type`, `difficulty`, `solver_code` |
| IndustryOR, OptMath | `id` | `en_question` | `en_answer` | `difficulty` |
| Mamo | `id` | `Question` | `Answer` | `Category`, `Type` |
| NL4Opt, NL4LP | `id` | `question` | `answer` | — |
| OptiBench | `id` | `question` | `results` | `type` |

## Dataset version

The released OptMath subset contains 128 records. Table II of the paper reports 129. See [dataset licenses and attribution](DATA_LICENSES.md) for upstream sources and changes to the released data.
