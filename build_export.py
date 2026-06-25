#!/usr/bin/env python3
"""Assemble all per-product files in output/ into a single export.json, and validate.

Run from the gen-task/ folder after every product has an output/<sid>.json:

    python build_export.py

Produces export.json (a JSON array, ready to import) and prints a validation report.
"""
import json, glob, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "output")
media = json.load(open(os.path.join(ROOT, "media.json"), encoding="utf-8"))

# expected sids from products.csv
import csv
csv.field_size_limit(10**8)
rows = list(csv.DictReader(open(os.path.join(ROOT, "products.csv"), encoding="utf-8")))
expected = {int(r["sid"]) for r in rows}

items, problems = [], []
seen = set()
for f in sorted(glob.glob(os.path.join(OUT, "*.json"))):
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        problems.append(f"{os.path.basename(f)}: INVALID JSON ({e})"); continue
    sid = d.get("sid"); seen.add(sid)
    desc = d.get("avs_description", "") or ""
    feats = d.get("features", []); ntk = d.get("ntk", [])
    m = media.get(str(sid), {"images": [], "videos": []})
    n_img, n_vid = len(m["images"]), len(m["videos"])
    flags = []
    if "[[IMG" in desc: flags.append("leftover [[IMGn]] marker")
    got_img = desc.count("<img")
    if got_img != n_img: flags.append(f"images {got_img}/{n_img}")
    got_vid = desc.count("<iframe")
    if got_vid != n_vid: flags.append(f"videos {got_vid}/{n_vid}")
    if len(feats) < 3: flags.append(f"features={len(feats)}")
    if len(ntk) < 3: flags.append(f"ntk={len(ntk)}")
    if flags: problems.append(f"sid {sid}: " + "; ".join(flags))
    items.append(d)

missing = expected - seen
if missing:
    problems.append(f"MISSING {len(missing)} products: {sorted(missing)[:20]}{'...' if len(missing)>20 else ''}")

json.dump(items, open(os.path.join(ROOT, "export.json"), "w", encoding="utf-8"), ensure_ascii=False)
print(f"export.json written: {len(items)} products (expected {len(expected)})")
if problems:
    print(f"\n{len(problems)} PROBLEM(S) — fix the listed files and re-run:")
    for p in problems[:60]:
        print("  -", p)
    sys.exit(1)
print("ALL CHECKS PASSED.")
