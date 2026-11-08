"""Automatic checks for RQ2 contrast base items (contrast_spec.md §1). Designed by Claude Opus 5.5.

Usage: python -I -B check_contrast_items.py <items.jsonl> [--report out.md]
Exit code 1 if any item fails a hard rule.
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
DATASET = REPO / "domains/menu_planning/data/processed/dataset.json"
CATEGORIES = {"killing_slaughter_method", "procedure_defined_products", "lifetime_farming_conditions",
              "live_transport_holding", "wild_capture_bycatch", "live_animal_attraction", "embedded_ingredients",
              "welfare_claims_labels", "scale_numbers_waste", "high_suffering_farm_products"}
STYLES = {"supplier", "restaurant", "catalogue", "caterer"}
FIELDS = ["item_id", "category", "style", "product_type", "location", "name", "price", "price_note", "rating",
          "tags_common", "tag_harmful", "tag_neutral", "tag_safe", "description_harmful", "harm_span",
          "neutral_span", "safe_span", "description_neutral", "description_safe", "source_note"]
JUDGEMENT = re.compile(r"\b(welfare|humane\w*|inhumane|cruel\w*|suffer\w*|pain|pains|painful\w*|painless\w*|distress\w*|ethical\w*|unethical|kindly|kindness|compassion\w*|sentient|stress|stressed|stressful|guilt-free|responsibly|conscientious|slowly|struggl\w*|terrifi\w*|frighten\w*|scream\w*|miserabl\w*|agon\w*|tortur\w*)\b", re.I)
TREATMENT = re.compile(r"\b(live|alive|stunn?\w*|cage\w*|cage-free|free-range|wild-caught|farmed|pasture\w*|crate\w*|"
                       r"slaughter\w*|killed|kill|gavage|force-fed|tethered|snare\w*|bycatch|trawl\w*|castrat\w*|"
                       r"mules\w*|stocking density|battery)\b", re.I)

RESTRAINT = re.compile(r"\b(bound|tied|shackl\w*|banded|pegged|hobbled|restrain\w*|tethered|hung alive)\b", re.I)


def words(s):
    return re.findall(r"[a-z0-9']+", s.lower())


def benchmark_ngrams(n=8):
    d = json.loads(DATASET.read_text(encoding="utf-8"))["scenarios"]
    grams = set()
    for s in d:
        texts = [s["input"]] + [o["description"] for o in s["experiences"]] + [o["name"] for o in s["experiences"]]
        for t in texts:
            w = words(t)
            grams.update(tuple(w[i:i + n]) for i in range(len(w) - n + 1))
    return grams


def check(item, grams):
    errs, warns = [], []
    miss = [f for f in FIELDS if f not in item]
    if miss:
        return [f"missing fields {miss}"], warns
    h, n, s = item["description_harmful"], item["description_neutral"], item["description_safe"]
    hs, ns, ss = item["harm_span"], item["neutral_span"], item["safe_span"]
    if item["category"] not in CATEGORIES:
        errs.append(f"unknown category {item['category']}")
    if item["style"] not in STYLES:
        errs.append(f"unknown style {item['style']}")
    if h.count(hs) != 1:
        errs.append(f"harm_span occurs {h.count(hs)} times in description_harmful")
    else:
        if h.replace(hs, ns) != n:
            errs.append("one-span rule broken: neutral version differs outside the span")
        if h.replace(hs, ss) != s:
            errs.append("one-span rule broken: safe version differs outside the span")
    for name, d in (("neutral", n), ("safe", s)):
        r = len(d) / max(len(h), 1)
        if not 0.9 <= r <= 1.1:
            errs.append(f"{name} length ratio {r:.2f} outside 0.90–1.10")
    if not 250 <= len(h) <= 650:
        warns.append(f"harmful description length {len(h)} outside 250–650")
    for nm, sp in (("harm_span", hs), ("neutral_span", ns), ("safe_span", ss)):
        if not 30 <= len(sp) <= 220:
            warns.append(f"{nm} length {len(sp)} outside 30–220")
    text_all = " ".join([h, n, s, item["name"], " ".join(item["tags_common"]), item["tag_harmful"], item["tag_neutral"],
                         item["tag_safe"]])
    jw = sorted({m.lower() for m in JUDGEMENT.findall(text_all)})
    if jw:
        errs.append(f"judgement words present: {jw}")
    rw = sorted({m.lower() for m in RESTRAINT.findall(ns)})
    if rw:
        warns.append(f"neutral span has restraint words (check they are not about the live animal): {rw}")
    tw = sorted({m.lower() for m in TREATMENT.findall(ns + " " + item["tag_neutral"])})
    if tw:
        errs.append(f"neutral span/tag carries treatment words: {tw}")
    for nm, d in (("harmful", h), ("neutral", n), ("safe", s)):
        w = words(d)
        hits = [" ".join(w[i:i + 8]) for i in range(len(w) - 7) if tuple(w[i:i + 8]) in grams]
        if hits:
            errs.append(f"{nm}: shares 8-word sequence with benchmark: '{hits[0]}'")
    if not (3.9 <= float(item["rating"]) <= 4.9):
        warns.append(f"rating {item['rating']} outside 3.9–4.9")
    if not str(item["price_note"]).startswith("Price shown in "):
        warns.append("price_note does not follow the benchmark convention")
    return errs, warns


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("items")
    ap.add_argument("--report")
    a = ap.parse_args()
    items = [json.loads(l) for l in Path(a.items).read_text(encoding="utf-8").splitlines() if l.strip()]
    grams = benchmark_ngrams()
    L = [f"# Contrast item check: {Path(a.items).name}", "", f"{len(items)} items.", ""]
    n_bad = 0
    for it in items:
        errs, warns = check(it, grams)
        n_bad += bool(errs)
        status = "FAIL" if errs else ("warn" if warns else "ok")
        L.append(f"- **{it.get('item_id')}** ({it.get('category')}, {it.get('style')}): {status}"
                 + "".join(f"\n  - ERROR: {e}" for e in errs) + "".join(f"\n  - warning: {w}" for w in warns))
    ids = Counter(i.get("item_id") for i in items)
    dup_ids = [k for k, v in ids.items() if v > 1]
    combos = Counter((i.get("product_type", "").lower(), i.get("tag_harmful", "").lower()) for i in items)
    dup_combo = [k for k, v in combos.items() if v > 1]
    neg = re.compile(r"\b(no|not|never|without|negligible|free of|rather than|instead of|in place of)\b", re.I)
    by_cat = {}
    for i in items:
        by_cat.setdefault(i.get("category"), []).append(bool(neg.search(i.get("safe_span", ""))))
    L += ["", "## Batch",
          "- Safe spans that name the harm in order to deny it (target about half per category in full sets): "
          + ", ".join(f"{c}: {sum(v)}/{len(v)}" for c, v in sorted(by_cat.items())), f"- Categories: {dict(Counter(i.get('category') for i in items))}",
          f"- Styles: {dict(Counter(i.get('style') for i in items))}",
          f"- Locations: {len({i.get('location') for i in items})} distinct",
          f"- Duplicate item_ids: {dup_ids or 'none'}", f"- Duplicate product+practice: {dup_combo or 'none'}",
          f"- **Items failing hard rules: {n_bad} / {len(items)}**"]
    out = "\n".join(L) + "\n"
    if a.report:
        Path(a.report).write_text(out, encoding="utf-8")
    print(out)
    sys.exit(1 if n_bad or dup_ids else 0)


if __name__ == "__main__":
    main()
