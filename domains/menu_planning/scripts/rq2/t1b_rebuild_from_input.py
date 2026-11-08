"""T1b: validate request_from_event (rebuild from event.input) and write t1_per_call.csv."""
import json, glob, csv, os, sys, collections
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inspect_ai.log import read_eval_log
from transformers import AutoTokenizer
from replay_rebuild import render, request_from_event

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, "../../../../results/logs/full/qwen3.5-9b")
OUT = os.path.join(HERE, "../../../../../rq2_work/outputs/t1")
ids = {d["scenario_id"] for d in json.load(open(os.path.join(HERE, "../../../../results/rq2/tuning_scenarios.json")))}
VARIANTS = ["base", "price_swap", "rating_swap", "reversed"]
ok = lambda sid: any(str(sid) == f"{i}_{v}" for i in ids for v in VARIANTS)
tok = AutoTokenizer.from_pretrained("Qwen/Qwen3.5-9B")

rows = []; a_mis = 0; a_n = 0; b_mis = 0; b_n = 0; b_diffs = []; msg_mis = 0
missing_idx = collections.Counter(); missing_last = 0; missing_final_order = 0
for cond in ["neutral", "ethical"]:
    log = read_eval_log(glob.glob(f"{REPO}/{cond}/*.eval")[0], resolve_attachments=True)
    for s in log.samples:
        if not ok(s.id): continue
        evs = [e for e in s.events if e.event == "model"]
        def donor(i):  # nearest earlier logged request, else nearest later one (never the event's own)
            for j in list(range(i - 1, -1, -1)) + list(range(i + 1, len(evs))):
                if j != i and evs[j].call is not None: return evs[j].call.request
        for i, e in enumerate(evs):
            prev = donor(i)
            logged = e.output.usage.input_tokens
            rebuilt_req = request_from_event(e, prev)
            ids_rebuilt = render(rebuilt_req, tok)
            if e.call is not None:
                ids_logged = render(e.call.request, tok)
                a_n += 1
                if ids_rebuilt != ids_logged: a_mis += 1
                if rebuilt_req["messages"] != e.call.request["messages"]: msg_mis += 1
                src = "logged_request"; n_used = len(ids_logged)
            else:
                src = "rebuilt_from_input"; n_used = len(ids_rebuilt)
                b_n += 1; b_diffs.append(n_used - logged); b_mis += (n_used != logged)
                missing_idx[i] += 1
                if i == len(evs) - 1: missing_last += 1
                if any(tc.function == "place_order" for tc in (e.output.choices[0].message.tool_calls or [])): missing_final_order += 1
            rows.append([str(s.id), s.epoch, cond, i, logged, n_used, n_used - logged, src])
print(f"(a) logged-request calls: {a_n}; token-ID mismatches rebuilt-vs-logged: {a_mis}; message-dict mismatches: {msg_mis}")
print(f"(b) no-request calls: {b_n}; count mismatches vs usage.input_tokens: {b_mis}; diffs {collections.Counter(b_diffs)}")
print("missing call_index distribution", dict(sorted(missing_idx.items())), "last-call:", missing_last, "producing place_order:", missing_final_order)
print("total rows", len(rows), "exact", sum(r[6] == 0 for r in rows))
with open(os.path.join(OUT, "t1_per_call.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["sample_id","epoch","prompt_condition","call_index","logged_input_tokens","rebuilt_tokens","diff","source"])
    w.writerows(rows)
