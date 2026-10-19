# Synthcase Forge

[Français](README.md) · [Español](README.es.md)

**Create rare cases with known answers, then find the smallest change that flips an answer.**

OR-Tools generates constrained cases under explicit cohort quotas. An independent Python checker recomputes rules, products and labels. A minimal variant flips a label without changing immutable facts. Data export to SQLite with foreign keys and label indexes.

![Synthetic cases and verified minimal variant](docs/preview-fr.png)

## Try it

Python 3.11 or newer. No key for generation, checking or exploration.

```sh
python3 -m venv .venv
.venv/bin/pip install .
.venv/bin/python -m synthcase serve --lang en
```

Open `http://127.0.0.1:8767/?lang=en`. The example has twelve cases: four without declared discrepancies, three quantity discrepancies, three price discrepancies and two combined. Select a case: the solver minimizes changed fields, then their distance, and recomputes derived totals. Order, receipt and agreed price remain frozen.

```sh
.venv/bin/python -m synthcase generate synthcase/examples/invoice-cases.json --seed 7 --output .local/data.json
.venv/bin/python -m synthcase pair .local/data.json case-0005 quantity_exceeds_receipt
.venv/bin/python -m synthcase export .local/data.json .local/cases.sqlite
```

Export refuses to overwrite an existing database. UI and CLI messages support FR/EN/ES.

## Inspectable specification

- `variables`: integer bounds per field;
- `constraints`: linear predicates, conjunctions, disjunctions and negation;
- `products`: derived fields, such as quantity × price;
- `labels`: truth defined by these predicates, never by a model;
- `cohorts`: exact counts and required labels;
- `immutable`: facts preserved in variants.

The invoice example is one specification, not a tax-compliance assertion. Up to twenty variables and one hundred cases per request; rows are distinct. Impossible rules or exhausted domains produce `partial` with missing quotas and a sufficient conflict when available; conflicts need not be minimal.

The seed sets random targets the solver tries to approach. This is **neither uniform sampling nor a representative distribution of real invoices**. Time-bounded solving may return `FEASIBLE`, whose result can differ across machines; each row keeps `solve_status`. Variant minimality is claimed only when proven and concerns independent fields; derived changes appear separately.

## Jev assesses plausibility without redefining truth

Optional review makes **one call, at most six questions**, selecting one representative per cohort. It asks `plausible / implausible / uncertain`, retains probabilities and routes low-confidence opinions to review. Opinions never modify computed labels. The browser calls no model and exposes no key route.

```sh
.venv/bin/python -m synthcase review .local/data.json --lang en --output .local/opinions.json
```

Transport reads `TYPESAFE_API_KEY` from the environment. Explicit `--env .env` only accepts a Git-ignored file with permissions `600`. Keys, headers and provider error bodies are never displayed. TLS verification remains enabled with certifi certificates; authenticated redirects are not followed.

Live check on October 19, 2026: Jev `jev-1.13.0` judged three representatives plausible with confidences **1.00 / 0.72 / 0.58**, using **1,044 input and 147 output tokens**. The latter two require review under the declared 0.8 threshold. This verifies transport and opinion separation, **not general model quality or dataset realism**. Generation, tests and CI remain offline; no key is published.

## Existing tools and limits

[SDV](https://docs.sdv.dev/sdv/modeling/constraint-augmented-generation-cag.md) already supports constrained synthetic generation. This project does not invent that principle: it focuses a small demo on **rare-case quotas → known labels → minimum-intervention variant → separate plausibility review**. [OR-Tools](https://developers.google.com/optimization/cp) supplies solving; [TypeSafe Choice](https://docs.typesafe.ai/primitives/choice) supplies optional opinions.

A label is true only relative to its supplied rule. Incomplete rules can yield implausible situations. Variants change records under declared equations; they are neither executable business actions nor causal evidence. No differential privacy, source-distribution preservation, legal validation or SOTA superiority is claimed.

## Validation

```sh
.venv/bin/python -m unittest discover -s tests -v
npm ci
npx playwright install chromium
PYTHON=.venv/bin/python npm run test:browser
npm run format:check
```

Fourteen tests cover quotas, products, labels, uniqueness, impossibility, counterfactuals against exhaustive enumeration, SQLite export and simulated Jev review. Browser checks FR/EN/ES, mobile, quotas and absence of secret routes; CI checks Python 3.11/3.12 and wheel installation outside sources. Exit 1 denotes partial generation or impossible variants, 2 denotes invalid input/transport. MIT license; research alpha.
