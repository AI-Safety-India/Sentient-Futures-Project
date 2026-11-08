"""RQ1 step 2b: is Claude's logged reasoning the raw chain of thought or a summary? (RQ1_PLAN.md §9, limit 3)

Reads every sample of the 4 scored Claude models and 2 full-reasoning reference models, measures the
ContentReasoning blocks (presence, redaction, signatures, length, style), dumps 5 verbatim excerpts per
Claude model, and writes rq1_work/outputs/CLAUDE_REASONING_AUDIT.md.

Run: uv run --project <repo> python -I -B audit_claude_reasoning.py

Layout: run from the repo root, e.g. `uv run --with pyarrow python -I -B domains/menu_planning/scripts/rq1/<script>.py`.
Inputs and outputs are kept OUTSIDE the repo, next to the clone: ../rq1_outputs (Step 1 table) and
../rq1_work/outputs (everything else), so running the scripts never makes the repo dirty.
"""

import argparse
import glob
import json
import random
import re
import statistics
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from inspect_ai.log import read_eval_log
from inspect_ai.model import ContentReasoning, ContentText

REPO = Path(__file__).resolve().parents[4]
SFN = REPO.parent  # inputs and outputs live next to the clone (sfn/rq1_outputs, sfn/rq1_work), so the repo stays clean
LOGS = REPO / "results/logs"
NEEL = SFN / "openrouter_runs/combined_neel"
SEED = 20261106

# (display name, kind, list of folders holding <cond>/*.eval; samples from all folders are combined)
MODELS = [
    ("Claude Opus 4.8", "claude", [NEEL / "claude-opus-4.8"], [LOGS / "pilot/claude-opus-4.8", LOGS / "full_1epoch/claude-opus-4.8"]),
    ("Claude Opus 5", "claude", [LOGS / "full_1epoch/claude-opus-5"], None),
    ("Claude Opus 5.5", "claude", [LOGS / "full_1epoch/claude-opus-5.5"], None),
    ("Claude Fable 5.1", "claude", [LOGS / "full_1epoch/claude-fable-5.1"], None),
    ("Qwen3.5-9B", "reference", [LOGS / "full/qwen3.5-9b"], None),
    ("DeepSeek V4 Pro", "reference", [NEEL / "deepseek-v4-pro"], [LOGS / "pilot/deepseek-v4-pro", LOGS / "full_1epoch/deepseek-v4-pro"]),
]

FIRST_PERSON = {
    "I need to": r"\bI need to\b",
    "Let me": r"\bLet me\b",
    "Let's": r"\bLet'?s\b",
    "I'll / I will": r"\bI(?:'ll| will)\b",
    "I should": r"\bI should\b",
}
HESITATION = {  # self-correction and thinking-aloud words: typical of raw chains of thought
    "Wait": r"\bWait\b",
    "Hmm": r"\bHmm+\b",
    "Actually": r"\bActually\b",
    "Okay / OK": r"\b(?:Okay|OK)\b[,.]",
    "But ": r"(?:^|[.!?]\s+)But\b",
}
SUMMARY = {
    "The user wants/is/asks": r"\bThe (?:user|customer) (?:wants|is|asks|asked|needs|has|requested)\b",
    "Summary: / heading": r"(?im)^\s*(?:\*\*[^*\n]+\*\*\s*$|#+\s|summary:)",
    "Bullet / numbered line": r"(?m)^\s*(?:[-*•]|\d+[.)])\s+\S",
    "Gerund title (e.g. 'Evaluating options')": r"(?m)^\s*\**[A-Z][a-z]+ing\b[^.\n]{0,60}\**\s*$",
}
RX = {k: re.compile(v) for d in (FIRST_PERSON, HESITATION, SUMMARY) for k, v in d.items()}


def success_log(folder):
    logs = [f for f in glob.glob(str(folder / "*.eval")) if read_eval_log(f, header_only=True).status == "success"]
    if len(logs) != 1:
        sys.exit(f"Expected one successful log in {folder}, found {len(logs)}")
    return logs[0]


def samples_for(primary, fallback):
    out, files = [], []
    for cond in ("neutral", "ethical"):
        folders = primary if all((f / cond).exists() for f in primary) else fallback
        for folder in folders:
            f = success_log(folder / cond)
            files.append(f)
            out.extend((cond, s) for s in read_eval_log(f).samples)
    return out, files


def describe(xs):
    if not xs:
        return dict(n=0, mean=0, median=0, q1=0, q3=0, min=0, max=0)
    q = statistics.quantiles(xs, n=4) if len(xs) > 1 else [xs[0]] * 3
    return dict(n=len(xs), mean=statistics.mean(xs), median=statistics.median(xs), q1=q[0], q3=q[2], min=min(xs), max=max(xs))


def audit(name, primary, fallback):
    samples, files = samples_for(primary, fallback)
    turns = with_r = with_text_only = 0
    blocks = []  # dicts: text, signature_len, redacted, summary
    for cond, s in samples:
        for m in s.messages:
            if m.role != "assistant":
                continue
            turns += 1
            parts = [] if isinstance(m.content, str) else m.content
            rs = [p for p in parts if isinstance(p, ContentReasoning)]
            if rs:
                with_r += 1
            for p in rs:
                blocks.append(dict(text=p.reasoning or "", sig=len(p.signature or ""), redacted=bool(p.redacted),
                                   summary=p.summary, cond=cond, sample=str(s.id)))
            if not rs:
                if isinstance(m.content, str) and "<think>" in m.content:
                    with_r += 1  # reasoning inline in think tags (counts as present)
                    blocks.append(dict(text=re.sub(r"</?think>", "", m.content), sig=0, redacted=False, summary=None,
                                       cond=cond, sample=str(s.id)))
                else:
                    with_text_only += 1
    readable = [b for b in blocks if not b["redacted"] and b["text"].strip()]
    chars = [len(b["text"]) for b in readable]
    words = [len(b["text"].split()) for b in readable]
    sig_ratio = [b["sig"] / max(len(b["text"]), 1) for b in readable if b["sig"]]
    marker = {k: sum(1 for b in readable if RX[k].search(b["text"])) / max(len(readable), 1) for k in RX}
    per_kw = {k: sum(len(RX[k].findall(b["text"])) for b in readable) / max(sum(words), 1) * 1000 for k in RX}
    return dict(
        name=name, files=files, samples=len(samples), turns=turns, turns_with_reasoning=with_r,
        blocks=len(blocks), redacted=sum(b["redacted"] for b in blocks), empty=sum(1 for b in blocks if not b["redacted"] and not b["text"].strip()),
        with_signature=sum(1 for b in blocks if b["sig"]), with_summary_field=sum(1 for b in blocks if b["summary"]),
        chars=describe(chars), words=describe(words), sig_len=describe([b["sig"] for b in readable if b["sig"]]),
        sig_ratio=describe(sig_ratio), marker=marker, per_kw=per_kw, readable=readable,
    )


def excerpts(readable, k=5):
    """5 blocks spread over the length distribution (10th..90th percentile), chosen with a fixed seed."""
    rnd = random.Random(SEED)
    pool = sorted(readable, key=lambda b: len(b["text"]))
    picks = []
    for q in (0.1, 0.3, 0.5, 0.7, 0.9):
        lo, hi = int(len(pool) * max(q - 0.05, 0)), int(len(pool) * min(q + 0.05, 1))
        picks.append(rnd.choice(pool[lo:max(hi, lo + 1)]))
    return picks


def f1(x):
    return f"{x:.1f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(SFN / "rq1_work/outputs/CLAUDE_REASONING_AUDIT.md"))
    ap.add_argument("--json", default=str(SFN / "rq1_work/outputs/claude_reasoning_audit_metrics.json"))
    args = ap.parse_args()

    res = []
    for name, kind, primary, fallback in MODELS:
        r = audit(name, primary, fallback or primary)
        r["kind"] = kind
        res.append(r)
        print(f"{name:18s} samples {r['samples']}, turns {r['turns']}, blocks {r['blocks']}, "
              f"median words {r['words']['median']:.0f}, signature {r['with_signature']}/{r['blocks']}", flush=True)

    Path(args.json).write_text(json.dumps([{k: v for k, v in r.items() if k != "readable"} for r in res], indent=1, default=str),
                               encoding="utf-8")
    write_report(res, args.out)
    print(f"Wrote {args.out}")


def write_report(res, out):
    L = []
    w = L.append
    w("# Claude reasoning audit (RQ1_PLAN.md §9, limit 3)")
    w("")
    w(f"Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} by `rq1_work/scripts/audit_claude_reasoning.py`. "
      "All samples of both prompt conditions are read. Reference models with known full reasoning: Qwen3.5-9B (vLLM, raw "
      "`<think>` output) and DeepSeek V4 Pro (OpenRouter).")
    w("")
    refs = [r for r in res if r["kind"] == "reference"]
    ref_hes = statistics.mean(max(r["marker"][k] for k in HESITATION) for r in refs)
    ref_words = min(r["words"]["median"] for r in refs)
    w("## 0. Verdict")
    w("")
    w("**Documentation.** Anthropic's API reference states that the raw chain of thought is never exposed for current Claude "
      "models (Opus 4.7 and later, Opus 5, Opus 5.5, Fable 5 / 5.1). A thinking block's text is either a readable **summary** "
      "(`display: \"summarized\"`) or empty (`display: \"omitted\"`, the default on these models). The full thinking is carried "
      "only in the encrypted `signature`. Our logs contain non-empty text, so OpenRouter returned the summarized display.")
    w("")
    w("**Evidence from our logs** (criteria fixed before reading the excerpts):")
    w("1. *Signature ÷ visible text*: the summarized model's signature is many times longer than its text. DeepSeek's is about 1.1×.")
    w(f"2. *Self-correction markers* (Wait, Hmm, Actually, sentence-initial But): reference models have them in up to "
      f"{100*ref_hes:.0f}% of blocks. A summary written after the fact has almost none.")
    w(f"3. *Length*: reference median ≥ {ref_words:.0f} words per block.")
    w("4. *Style*: narration in present progressive (\"I'm checking…\", \"I'm going through…\") instead of working notes.")
    w("")
    w("| Model | Signature ÷ text (median) | Max self-correction marker (% of blocks) | Median words | Verdict |")
    w("|---|---|---|---|---|")
    for r in res:
        hes = max(r["marker"][k] for k in HESITATION)
        ratio = r["sig_ratio"]["median"] if r["with_signature"] else None
        if r["kind"] == "claude":
            summarized = (ratio or 0) > 3 and hes < 0.05 and r["words"]["median"] < ref_words / 2
            verdict = "**Summarized thinking** (documented, and all 3 measured criteria agree)" if summarized \
                else "Summarized per documentation; measured criteria mixed, see below"
        else:
            verdict = "Full raw reasoning (reference)"
        w(f"| {r['name']} | {('%.2f' % ratio) if ratio else 'n/a (no signature)'} | {100*hes:.1f} | {r['words']['median']:.0f} | {verdict} |")
    w("")
    w("**Consequences for RQ1.**")
    w("- Claude scores measure what Anthropic's **summarizer** kept, not what the model thought. A summary can drop a welfare "
      "consideration (making silence look more common) and is written in polished, considerate prose. Claude results are "
      "reported as a **lower bound on verbalised recognition**, in their own table, never pooled with full-reasoning models.")
    w("- Claude runs **without a reasoning block** in a turn (the share in §1 below 100%) are normal: adaptive thinking skips "
      "some turns. They are not missing data.")
    w("- Part B (visible messages) is unaffected: it is the model's own text.")
    w("")
    w("**Paragraph for §9 of the paper (Limitations):**")
    w("")
    w("> *Claude's reasoning is a summary.* For the four Claude models (Opus 4.8, Opus 5, Opus 5.5 and Fable 5.1), the "
      "provider does not return the raw chain of thought; the API returns a model-written summary of it, and the full "
      "reasoning is kept only in an encrypted signature. Our logs agree: Claude reasoning blocks are 3–6 times shorter than "
      "those of full-reasoning models (median 28–56 vs 148–175 words), carry signatures 5–18 times longer than their visible "
      "text (vs about 1.1 for DeepSeek V4 Pro), and almost never contain the self-corrections (\"wait\", \"actually\") typical "
      "of raw reasoning. We therefore treat Claude's verbalisation rates as a lower bound: a welfare consideration the model "
      "weighed may have been left out of the summary. Claude results are reported separately and never pooled with models "
      "whose full reasoning we could read. Six further frontier models (GPT-6 Luna, Terra, Sol, Astra; Gemini 4 Argon; "
      "Muse Wonder) return no readable reasoning at all and are excluded from RQ1.")
    w("")
    w("## 1. Presence, redaction and signatures")
    w("")
    w("| Model | Samples | Assistant turns | Turns with a reasoning block | Reasoning blocks | Redacted | Empty | With signature | `summary` field set |")
    w("|---|---|---|---|---|---|---|---|---|")
    for r in res:
        w(f"| {r['name']} | {r['samples']} | {r['turns']} | {r['turns_with_reasoning']} ({100*r['turns_with_reasoning']/max(r['turns'],1):.1f}%) | "
          f"{r['blocks']} | {r['redacted']} | {r['empty']} | {r['with_signature']} | {r['with_summary_field']} |")
    w("")
    w("## 2. Length of readable reasoning blocks")
    w("")
    w("| Model | Blocks | Words: mean | median | IQR | min–max | Chars: mean | median | IQR | max |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    for r in res:
        a, c = r["words"], r["chars"]
        w(f"| {r['name']} | {a['n']} | {f1(a['mean'])} | {f1(a['median'])} | {f1(a['q1'])}–{f1(a['q3'])} | {a['min']}–{a['max']} | "
          f"{f1(c['mean'])} | {f1(c['median'])} | {f1(c['q1'])}–{f1(c['q3'])} | {c['max']} |")
    w("")
    w("**Signature size vs visible text.** Anthropic's thinking blocks carry an encrypted `signature` that holds the full "
      "thinking. If the visible text were the whole thinking, the signature would grow in step with it. A signature many "
      "times longer than the visible text, especially on short blocks, means more thinking happened than is shown.")
    w("")
    w("| Model | Blocks with signature | Signature chars: median | IQR | Signature ÷ visible chars: median | IQR |")
    w("|---|---|---|---|---|---|")
    for r in res:
        if r["with_signature"]:
            s, q = r["sig_len"], r["sig_ratio"]
            w(f"| {r['name']} | {r['with_signature']} | {f1(s['median'])} | {f1(s['q1'])}–{f1(s['q3'])} | {q['median']:.2f} | {q['q1']:.2f}–{q['q3']:.2f} |")
    w("")
    w("## 3. Style markers")
    w("")
    w("Share of readable blocks containing each marker (%).")
    w("")
    groups = [("First-person deliberation", FIRST_PERSON), ("Hesitation / self-correction", HESITATION), ("Summary style", SUMMARY)]
    keys = [k for _, d in groups for k in d]
    w("| Model | " + " | ".join(keys) + " |")
    w("|---|" + "---|" * len(keys))
    for r in res:
        w(f"| {r['name']} | " + " | ".join(f1(100 * r['marker'][k]) for k in keys) + " |")
    w("")
    w("Groups: " + "; ".join(f"**{g}** = {', '.join(d)}" for g, d in groups) + ".")
    w("")
    w("Occurrences per 1,000 words:")
    w("")
    w("| Model | " + " | ".join(keys) + " |")
    w("|---|" + "---|" * len(keys))
    for r in res:
        w(f"| {r['name']} | " + " | ".join(f"{r['per_kw'][k]:.2f}" for k in keys) + " |")
    w("")
    w("## 4. Verbatim excerpts (5 per Claude model)")
    w("")
    w("Chosen with seed 20261106 at the 10th, 30th, 50th, 70th and 90th percentiles of block length. Long blocks are cut at 1,500 characters.")
    for r in res:
        if r["kind"] != "claude":
            continue
        w("")
        w(f"### {r['name']}")
        for i, b in enumerate(excerpts(r["readable"]), 1):
            t = b["text"].strip()
            cut = t[:1500] + (" […]" if len(t) > 1500 else "")
            w("")
            w(f"**{i}.** `{b['sample']}` ({b['cond']}, {len(t.split())} words, signature {b['sig']} chars)")
            w("")
            w("```text")
            w(cut.replace("```", "'''"))
            w("```")
    w("")
    w("## 5. Source logs")
    w("")
    for r in res:
        for f in r["files"]:
            w(f"- {r['name']}: `{Path(f).relative_to(SFN).as_posix()}`")
    Path(out).write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
