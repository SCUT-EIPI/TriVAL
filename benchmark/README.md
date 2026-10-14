# Benchmark data

The files in this directory are the project's prepared benchmark snapshots. Dataset IDs and instance values are preserved. Some third-party descriptions and reference answers were revised during preparation, and some records were excluded. These files are not byte-for-byte copies of every upstream release.

## Available datasets

| Runner name | Path | Records |
|---|---|---:|
| `nl4cop` | `NL4COP/*.json` | 150 |
| `industryor` | `IndustryOR.jsonl` | 99 |
| `mamo_complex` | `Mamo_complex.jsonl` | 210 |
| `mamo_easy` | `Mamo_easy.jsonl` | 642 |
| `optmath` | `Optmath.jsonl` | 128 |
| `optibench` | `OptiBench.jsonl` | 403 |
| `nl4opt` | `NL4Opt.jsonl` | 205 |
| `nl4lp` | `NL4LP.jsonl` | 178 |

NL4COP covers 50 problem types. Each type has one `simple`, one `medium`, and one `hard` instance, for 50 records at each difficulty.

`nl4lp` is the local runner name for the processed NLP4LP benchmark.

## Input and reference fields

Files use UTF-8. JSONL files contain one JSON object per non-empty line. NL4COP stores one JSON object per file.

| Dataset | ID | Problem input | Reference answer | Metadata |
|---|---|---|---|---|
| NL4COP | `problem_id` | `problem_description` | `reference_solution` | `problem_type`, `difficulty`, `solver_code` |
| IndustryOR, OptMath | `id` | `en_question` | `en_answer` | `difficulty` |
| Mamo | `id` | `Question` | `Answer` | `Category`, `Type` |
| NL4Opt, NL4LP | `id` | `question` | `answer` | — |
| OptiBench | `id` | `question` | `results` | `type` |

Reference answers may be strings, numbers, lists, or objects, depending on the dataset. Preserve their original types when reading the data.

In NL4COP:

- `problem_id`: stable record identifier.
- `problem_type`: problem family or type.
- `difficulty`: `simple`, `medium`, or `hard`.
- `problem_description`: complete natural-language problem.
- `reference_solution`: reference objective value and/or decision values.
- `solver_code`: reference Python solver implementation.

Reference answers and NL4COP reference code are dataset annotations. The single-problem runner sends only the problem input field to TriVAL.

## Record selection

`--index` selects one record using a zero-based position; it is not a dataset ID. JSONL readers preserve file order. The NL4COP reader sorts records by `problem_id`.

Run one record:

```bash
uv run python run.py --dataset nl4cop --index 0
```

Run one custom problem:

```bash
uv run python run.py --file examples/problem.txt
```

## Text normalization

Two NL4COP descriptions contained stray non-English characters. In `mkp_001`, the volume unit is written as `dm^3` (cubic decimeters). In `travelling_salesman_problem_001`, the grid description uses the word `precise`. Reference solutions and solver code are unchanged.

## Reference answer correction

NL4Opt record ID `49` had an empty reference answer. It is now filled as the string `"20.0"`. The optimal solution uses 10 cash-based ticket machines and 10 card-only machines. It processes 500 people per hour and uses 90 rolls of paper per hour. Exhaustive enumeration of the feasible integer machine counts confirms the optimum. The identical problem in the local NL4LP record ID `34` also has reference answer `"20.0"`. The question and record ID are unchanged.

## Dataset version

The released OptMath snapshot contains 128 records and excludes IDs `67` and `76`. An earlier 129-record version also included ID `67`. The manuscript's benchmark table reports 129; use the counts above for this released snapshot.

## Sources and use terms

Read [DATA_LICENSES.md](DATA_LICENSES.md) before redistributing or reusing these files. The implementation's MIT license does not replace third-party data licenses.

ComplexOR data is not included because its redistribution permission remains unconfirmed. Refer to the [upstream repository](https://github.com/xzymustbexzy/Chain-of-Experts).
