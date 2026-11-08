"""Merge the 10 category batches into one contrast base set, re-check everything, find near-duplicates,
apply Opus QA verdicts, and draw the 50-item human hand-check sample. Designed by Claude Opus 5.5.

Usage (from rq2_work/scripts):
  python -I -B assemble_contrast_set.py                 # merge + checks + near-duplicate report
  python -I -B assemble_contrast_set.py --apply-qa      # also drop items with a QA verdict of "drop"
Inputs : ../outputs/t3/full/<category>.jsonl, optional ../outputs/t3/qa/<category>_qa.jsonl
Outputs: ../outputs/t3/contrast_base_items.jsonl, ../outputs/t3/T6_ASSEMBLY_REPORT.md,
         ../outputs/t3/hand_check_50.csv (shared sheet for Prem and Neel)
"""

import argparse
import csv
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
T3 = HERE.parents[4].parent / "rq2_work" / "outputs" / "t3"
sys.path.insert(0, str(HERE))
import check_contrast_items as chk  # noqa: E402

SEED = 20261106


def shingles(text, n=6):
    w = chk.words(text)
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply-qa", action="store_true")
    a = ap.parse_args()

    items, missing = [], []
    for cat in sorted(chk.CATEGORIES):
        f = T3 / "qa" / f"{cat}_fixed.jsonl"  # the Opus-reviewed version, if QA has run
        if not f.exists():
            f = T3 / "full" / f"{cat}.jsonl"
        if not f.exists():
            missing.append(cat)
            continue
        items += [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
    grams = chk.benchmark_ngrams()
    pilot = [json.loads(l) for l in (T3 / "pilot_items.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]

    # hard-rule checks
    failing = {}
    for it in items:
        errs, _ = chk.check(it, grams)
        if errs:
            failing[it["item_id"]] = errs

    # near-duplicates: 6-word shingle Jaccard on the harmful description, across all items and against the pilot
    sh = {it["item_id"]: shingles(it["description_harmful"]) for it in items + pilot}
    ids = list(sh)
    near = []
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            x, y = sh[ids[i]], sh[ids[j]]
            if x and y:
                jac = len(x & y) / len(x | y)
                if jac >= 0.25:
                    near.append((round(jac, 2), ids[i], ids[j]))
    same_name = [k for k, v in Counter((it["name"].lower()) for it in items + pilot).items() if v > 1]

    # QA verdicts
    qa, dropped = {}, []
    qdir = T3 / "qa"
    if qdir.exists():
        for f in qdir.glob("*_qa.jsonl"):
            for l in f.read_text(encoding="utf-8").splitlines():
                if l.strip():
                    v = json.loads(l)
                    qa[v["item_id"]] = v
    final = []
    for it in items:
        v = qa.get(it["item_id"], {}).get("verdict")
        if it["item_id"] in failing or (a.apply_qa and v == "drop"):
            dropped.append(it["item_id"])
            continue
        final.append(it)
    # the 20 pilot items join the final set (they passed review)
    final_all = final + [p for p in pilot if p["item_id"] not in failing]

    out = T3 / "contrast_base_items.jsonl"
    out.write_text("".join(json.dumps(i, ensure_ascii=False) + "\n" for i in final_all), encoding="utf-8")

    # 50-item hand-check sample: 5 per category, stratified by style, from the final set
    rnd = random.Random(SEED)
    by_cat = defaultdict(list)
    for it in final:
        by_cat[it["category"]].append(it)
    sample = []
    for cat in sorted(by_cat):
        pool = sorted(by_cat[cat], key=lambda i: i["item_id"])
        rnd.shuffle(pool)
        styles_seen, pick = Counter(), []
        for it in pool:
            if len(pick) == 5:
                break
            if styles_seen[it["style"]] < 2:
                pick.append(it)
                styles_seen[it["style"]] += 1
        sample += pick
    with (T3 / "hand_check_50.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh, quoting=csv.QUOTE_ALL)
        w.writerow(["item_id", "category", "style", "description_harmful", "description_neutral", "description_safe",
                    "harm_span", "neutral_span", "safe_span", "source_note",
                    "harmful_really_harmful(Y/N)", "neutral_has_no_hint(Y/N)", "safe_really_avoids_it(Y/N)",
                    "realistic(Y/N)", "notes"])
        for it in sample:
            w.writerow([it[k] for k in ("item_id", "category", "style", "description_harmful", "description_neutral",
                                        "description_safe", "harm_span", "neutral_span", "safe_span", "source_note")]
                       + ["", "", "", "", ""])

    neg = re.compile(r"\b(no|not|never|without|negligible|free of)\b", re.I)
    L = ["# T6 assembly report", "",
         f"- Batches found: {10 - len(missing)} / 10" + (f" (missing: {missing})" if missing else ""),
         f"- Items written: {len(items)}; failing hard rules: {len(failing)}; QA verdicts loaded: {len(qa)}"
         + (f" ({dict(Counter(v['verdict'] for v in qa.values()))})" if qa else ""),
         f"- Dropped: {len(dropped)}; final set: {len(final_all)} (incl. {len(pilot)} pilot items)", "",
         "| Category | Items | supplier | restaurant | catalogue | caterer | Countries | Negated safe spans |",
         "|---|---|---|---|---|---|---|---|"]
    for cat in sorted(chk.CATEGORIES):
        s = [i for i in final_all if i["category"] == cat]
        st = Counter(i["style"] for i in s)
        countries = {i["location"].split(",")[-1].strip() for i in s}
        L.append(f"| `{cat}` | {len(s)} | {st['supplier']} | {st['restaurant']} | {st['catalogue']} | {st['caterer']} | "
                 f"{len(countries)} | {sum(bool(neg.search(i['safe_span'])) for i in s)} |")
    L += ["", "## Hard-rule failures"] + ([f"- {k}: {v}" for k, v in failing.items()] or ["- none"])
    L += ["", "## Near-duplicates (harmful description, 6-word shingle Jaccard ≥ 0.25)"] + (
        [f"- {j}: {x} / {y}" for j, x, y in sorted(near, reverse=True)] or ["- none"])
    L += ["", f"## Repeated business names: {same_name or 'none'}", "",
          f"Hand-check sheet: `hand_check_50.csv` ({len(sample)} items, 5 per category, seed {SEED})."]
    (T3 / "T6_ASSEMBLY_REPORT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
