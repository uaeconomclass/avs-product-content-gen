# AGENT TASK — Generate final, import-ready product content for AudioVS (289 products)

You are a capable Claude agent generating structured marketing content for an Australian
car-audio / 4x4 / vehicle-security retailer (AudioVS). For **every** product you produce three fields,
with images and videos already baked into the description, and write one JSON file per product.
The result must be **final and import-ready** — no post-processing.

Work **token-efficiently** — see WORKFLOW; do not load the whole CSV into context at once.

---

## INPUT (in this folder)

**`products.csv`** — one row per product:

| column | meaning |
|---|---|
| `sid` | staging product id — use as the output filename |
| `name` | product name |
| `n_images` | how many images belong in this product's description (0..N) |
| `key_features` | original "Key Features" bullets, joined by ` \| ` (may be empty) |
| `short` | short-description spec bullets, joined by ` \| ` (may be empty) |
| `src` | the **FULL** original product description (plain text, up to ~16k chars) |

**`media.json`** — `{ "<sid>": { "images": ["<img …>", …], "videos": ["<iframe …>", …] } }`.
The ready-to-use HTML media blocks for each product. Use them **verbatim** — never alter a `src`,
`width`, `height`, or any attribute. `images` are in document order; `videos` likewise.

**`example_output.json`** — a real finished file. Match its format and tone exactly.

## OUTPUT

For each product write **`output/<sid>.json`** (e.g. `output/573.json`), valid UTF-8 JSON:

```json
{
  "sid": 573,
  "avs_description": "<p>…</p>… (final HTML, media already embedded)",
  "features": [{"title": "", "text": ""}],
  "ntk": [{"question": "", "answer": ""}]
}
```

One file per product. **Never overwrite a file that already exists** (lets you resume after a stop).

---

## WHAT TO GENERATE

### 1. `avs_description` — final HTML string (the main Product Description)

- **Rewrite the FULL descriptive prose from `src`. Do NOT summarise, shorten, or drop information.**
  Keep all the content; use as many `<p>` paragraphs as needed, plus `<h3>`/`<h4>` subheadings and
  `<ul>` sub-lists where the source had that structure.
- Clean it up: remove junk/markup artefacts, fix wording, tidy formatting.
- **British-Australian spelling** throughout: manoeuvre, aluminium, colour, optimise, centre, fibre…
- Leave **OUT** only two things (they live in other fields): (a) the "Key Features" bullet list,
  (b) any raw spec-dump table. Everything else from `src` stays.
- **EMBED MEDIA (this is the key step — output must be final):**
  - **Images:** take this product's `media.json` → `images` array and insert **every** block,
    **verbatim**, in order, at sensible spots in the description (each on its own line between the
    paragraphs it best illustrates). Use all of them; the count of `<img` tags in your
    `avs_description` MUST equal `n_images`.
  - **Videos:** take `media.json` → `videos` and append **every** block, **verbatim**, at the very
    **end** of the description (after the last paragraph).
  - Do not invent, rewrite, or drop any media block. Do not add media that isn't in `media.json`.
  - If a product has no images / no videos, embed none.

### 2. `features` — array of `{title, text}`

- One entry per **meaningful** Key Feature. `title` = key term (short, Title Case); `text` = one short
  sentence (may be empty if the bullet is a pure spec).
- **Minimum 3.** If `key_features` is empty or just a raw spec dump, **derive** 3+ meaningful,
  customer-facing features from `src`/`short`. If more than 3 genuinely distinct features exist,
  include them all — do not cap at 3.

### 3. `ntk` — "Everything you need to know" Q&A, array of `{question, answer}`

- **Minimum 3** natural buyer questions with helpful answers.
- **Base answers ONLY on facts in `src`.** Do NOT invent warranty periods, prices, exact vehicle-model
  compatibility, certifications, or numbers not in the source. When unsure, stay general
  ("contact us to confirm fitment for your vehicle" is fine).

---

## STYLE

Marketing-tight but factual. Clear and confident, not flowery. British-Australian English everywhere.
Rewrite the source cleanly — keep all information, don't echo raw text verbatim (media blocks are the
only thing copied verbatim).

---

## WORKFLOW (token-optimised — follow this)

Do **not** read all of `products.csv` into context at once (~1.2 MB). Process in small chunks:

1. Take a chunk of ~8–10 unprocessed rows — extract just those rows (e.g. a one-liner printing rows
   `[i:i+10]` as JSON). Only those enter context. Read each chunk's products' media from `media.json`.
2. For each row: generate the three fields (with media embedded) and **immediately** write
   `output/<sid>.json`. Write the moment the product is done — never batch writes to the end.
3. Skip any product whose `output/<sid>.json` already exists (resume support).
4. Repeat until all 289 files exist.

Keep reasoning short — the value is the output files, not prose. Don't re-read written files or re-read
the whole CSV between chunks.

## FINISH — produce the import-ready artifact

When all 289 files exist, run:

```
python build_export.py
```

It assembles `output/*.json` into **`export.json`** (the final import-ready array) and validates every
product: valid JSON, 4 keys, `<img>` count == `n_images`, `<iframe>` count == video count, no leftover
`[[IMG]]` markers, `features` ≥ 3, `ntk` ≥ 3, none missing. **Fix anything it reports and re-run until it
prints `ALL CHECKS PASSED.`**

Then reply with: total products, that `export.json` passed all checks, and any product where you had to
derive features from scratch. `export.json` is the deliverable.

---

## DELIVERY — propose your work as a Pull Request (do NOT push to `master`)

This is a public repo; changes are reviewed before they land. Deliver your results as a PR, never by
committing to `master` directly.

1. Before you start (or before your first commit), create a branch:
   ```
   git checkout -b gen/<short-name>      # e.g. gen/claude-run-1
   ```
   If you don't have write access to this repo, **fork it first** (`gh repo fork --clone`) and branch
   in your fork.
2. When `build_export.py` prints `ALL CHECKS PASSED`, commit your work on that branch:
   ```
   git add output export.json
   git commit -m "Generate product content for all 289 products"
   git push -u origin gen/<short-name>
   ```
3. Open a pull request describing what you did:
   ```
   gh pr create --fill --title "Product content: all 289 products" \
     --body "Generated avs_description + features + ntk for 289 products. build_export.py: ALL CHECKS PASSED. Notes: <products where features were derived, anything skipped>."
   ```
4. Reply with the PR URL.

Anyone may run this task and open their own PR — improvements and re-runs are welcome.
