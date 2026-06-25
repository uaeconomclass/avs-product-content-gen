# AudioVS — Product Content Generation Task

A self-contained handoff package for an AI agent (Claude) to generate clean, import-ready
product content for the AudioVS catalogue (289 products): a rewritten **Product Description**
with images/videos embedded, a **Features** list, and an **Everything-You-Need-To-Know** Q&A.

## How to run

Point a capable Claude agent at this folder and tell it:

> Read `AGENT.md` and complete the task in full.

The agent reads `products.csv` + `media.json`, writes one `output/<sid>.json` per product, then runs
`build_export.py` to assemble and validate **`export.json`** — the final, import-ready deliverable.

## Contents

| file | role |
|---|---|
| `AGENT.md` | full instructions for the agent (the contract) |
| `products.csv` | all 289 products: `sid, name, n_images, key_features, short, src` (full description) |
| `media.json` | ready-to-embed `<img>` / `<iframe>` blocks per product `sid` |
| `example_output.json` | one finished file — format & tone reference |
| `build_export.py` | assembles `output/*.json` → `export.json` and validates everything |
| `output/` | the agent writes `<sid>.json` here (one per product) |
| `export.json` | **deliverable** — produced by `build_export.py` when all products are done |

## Output shape (per product)

```json
{
  "sid": 573,
  "avs_description": "<p>… final HTML, media embedded …</p>",
  "features": [{"title": "…", "text": "…"}],
  "ntk": [{"question": "…", "answer": "…"}]
}
```

## Validation (run by `build_export.py`)

- valid JSON, all four keys present
- `<img>` count in the description equals the product's `n_images`
- `<iframe>` (video) count equals the product's video count
- no leftover `[[IMG]]` markers
- `features` ≥ 3, `ntk` ≥ 3
- all 289 products present

The agent must iterate until it prints `ALL CHECKS PASSED.`

## Contributing — open to anyone

This repo is public and changes are reviewed before they land. The agent (or any contributor) delivers
results as a **pull request**, never by pushing to `master`:

1. Branch (`git checkout -b gen/<short-name>`), or fork the repo if you lack write access.
2. Generate the content, run `build_export.py` until it passes.
3. Commit `output/` + `export.json`, push the branch, and open a PR (`gh pr create --fill`).

Anyone is welcome to run the task and propose their own results — re-runs and improvements are reviewed
via PR. See `AGENT.md` → *DELIVERY* for the exact steps.
