import json, glob, csv, os, sys, collections

# Repo copy: run from the repo root, e.g. `uv run --with transformers --with jinja2 python -I -B domains/menu_planning/scripts/rq2/<script>.py`.
# Inputs/outputs live next to the clone in ../rq2_work (outside the repo, so it stays clean).
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inspect_ai.log import read_eval_log
from transformers import AutoTokenizer
import transformers, tokenizers
from replay_rebuild import render

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, "../../../../results/logs/full/qwen3.5-9b")
OUT = os.path.join(HERE, "../../../../../rq2_work/outputs/t1")
ids = {d["scenario_id"] for d in json.load(open(os.path.join(HERE, "../../../../results/rq2/tuning_scenarios.json")))}
VARIANTS = ["base", "price_swap", "rating_swap", "reversed"]
def ok(sid):
    s = str(sid)
    return any(s == f"{i}_{v}" for i in ids for v in VARIANTS)

tok = AutoTokenizer.from_pretrained("Qwen/Qwen3.5-9B")
calls = []  # (sid, epoch, cond, idx, logged, request)
for cond in ["neutral", "ethical"]:
    f = glob.glob(f"{REPO}/{cond}/*.eval")[0]
    log = read_eval_log(f, resolve_attachments=True)
    for s in log.samples:
        if not ok(s.id): continue
        evs = [e for e in s.events if e.event == "model" and e.call]
        for i, e in enumerate(evs):
            calls.append((str(s.id), s.epoch, cond, i, e.output.usage.input_tokens, e.call.request))
print("calls", len(calls), "samples", len({(c[0], c[1], c[2]) for c in calls}))

VAR = {
 "A raw (reasoning key, str args, OpenAI tools)": dict(rename_reasoning=False, parse_args=False),
 "B + rename reasoning->reasoning_content": dict(rename_reasoning=True, parse_args=False),
 "C + parsed args (no rename)": dict(rename_reasoning=False, parse_args=True),
 "D rename + parsed args (final)": dict(),
 "E D + inner function tools": dict(tools_inner=True),
 "G D, reasoning dropped": dict(drop_reasoning=True),
 "H D + enable_thinking=False": dict(template_kwargs={"enable_thinking": False}),
 "I D + reasoning_effort=medium kwarg": dict(template_kwargs={"reasoning_effort": "medium"}),
 "F D + content ''->None": dict(none_content=True),
}
results = {}
for name, kw in VAR.items():
    diffs = []
    for c in calls:
        try: n = len(render(c[5], tok, **kw))
        except Exception as ex: n = None
        diffs.append(None if n is None else n - c[4])
    m = sum(d == 0 for d in diffs)
    results[name] = (m, diffs)
    samp = {}
    for c, d in zip(calls, diffs):
        k = (c[0], c[1], c[2]); samp[k] = samp.get(k, True) and d == 0
    print(f"{name}: {m}/{len(calls)} calls, {sum(samp.values())}/{len(samp)} samples; diffs", dict(collections.Counter(diffs).most_common(6)))
best = "D rename + parsed args (final)"
print("best", best)
os.makedirs(OUT, exist_ok=True)
# per-call CSV is written by t1b_rebuild_from_input.py (covers all 1248 calls)
json.dump({"versions": {"transformers": transformers.__version__, "tokenizers": tokenizers.__version__},
           "variants": {k: v[0] for k, v in results.items()}, "n_calls": len(calls), "best": best},
          open(os.path.join(OUT, "t1_summary.json"), "w"), indent=1)
