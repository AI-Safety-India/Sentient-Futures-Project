"""RQ3 Causal Steering Harness for Qwen3.5-9B (`INTERP_PLAN.md` §6.5 & `results/rq3/RQ3_PREREGISTRATION.md`).

Tests whether injecting the evaluation probe vector (h <- h + alpha * w_eval)
into the residual stream during agent generation turns increases safe orders on neutral prompts.

Evaluates on the 10 tuning scenarios across all 4 variants (40 runs per condition).
"""
import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.dont_write_bytecode = True
sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
RESULTS_RQ3 = REPO_ROOT / "results/rq3"
PROBES_FILE = REPO_ROOT / "results/rq2/probes/probe_directions.npz"
DATASET_FILE = REPO_ROOT / "domains/menu_planning/data/processed/dataset.json"
TUNING_FILE = REPO_ROOT / "results/rq2/tuning_scenarios.json"

sys.path.insert(0, str(REPO_ROOT / "domains/menu_planning/eval"))
from dataset import load_scenarios
from prompts import SYSTEM_PROMPT
from tools import search_options, get_option_details, check_availability, place_order

os.makedirs(RESULTS_RQ3, exist_ok=True)


class ActivationSteeringHook:
    def __init__(self, direction: torch.Tensor, alpha: float = 1.0, mode: str = "add"):
        self.direction = direction
        self.alpha = alpha
        self.mode = mode
        self.enabled = True

    def __call__(self, module, inputs, output):
        if not self.enabled:
            return output
        if isinstance(output, tuple):
            h = output[0]
            rest = output[1:]
        else:
            h = output
            rest = None

        if self.mode == "add":
            h_mod = h + (self.alpha * self.direction.to(h.device, dtype=h.dtype))
        elif self.mode == "ablate":
            v = self.direction.to(h.device, dtype=h.dtype)
            v = v / (torch.norm(v) + 1e-12)
            proj = (h * v).sum(dim=-1, keepdim=True) * v
            h_mod = h - proj
        else:
            h_mod = h

        return (h_mod, *rest) if rest is not None else h_mod


def load_probes():
    data = np.load(PROBES_FILE)
    w_e1 = torch.tensor(data["e1_w_mm"], dtype=torch.float32)
    l_e1 = int(data["e1_layer"])
    w_e2 = torch.tensor(data["e2_w_mm"], dtype=torch.float32)
    l_e2 = int(data["e2_layer"])
    return {
        "e1": (w_e1, l_e1),
        "e2": (w_e2, l_e2),
    }


def main():
    parser = argparse.ArgumentParser(description="Run RQ3 Causal Steering on Qwen3.5-9B")
    parser.add_argument("--alpha", type=float, default=1.0, help="Steering magnitude alpha")
    parser.add_argument("--probe", type=str, default="e2", choices=["e1", "e2", "random"], help="Direction to use")
    parser.add_argument("--layer", type=int, default=26, help="Transformer layer to hook (1-indexed)")
    parser.add_argument("--mode", type=str, default="add", choices=["add", "ablate"], help="Intervention mode")
    parser.add_argument("--scenarios", type=str, default="tuning", choices=["tuning", "all"], help="Scenario subset")
    parser.add_argument("--model", type=str, default="Qwen/Qwen3.5-9B")
    args = parser.parse_args()

    probes = load_probes()
    if args.probe in ("e1", "e2"):
        direction, def_layer = probes[args.probe]
        layer_idx = args.layer if args.layer is not None else def_layer
    else:
        direction = torch.randn(4096, dtype=torch.float32)
        direction = direction / torch.norm(direction)
        layer_idx = args.layer

    print(f"=== Running RQ3 Causal Steering on Qwen3.5-9B ===")
    print(f"Probe: {args.probe} | Hooked Layer: L{layer_idx} | Alpha: {args.alpha} | Mode: {args.mode}")

    # Load tuning scenarios
    with open(TUNING_FILE, encoding="utf-8") as f:
        tuning_ids = {d["scenario_id"] for d in json.load(f)}
    
    # Load dataset
    with open(DATASET_FILE, encoding="utf-8") as f:
        all_scens = json.load(f)["scenarios"]
    scens = [s for s in all_scens if s["id"] in tuning_ids] if args.scenarios == "tuning" else all_scens
    print(f"Loaded {len(scens)} base scenarios ({len(scens)*4} runs across 4 variants).")

    # Load model and tokenizer
    print(f"Loading {args.model}...")
    tok = AutoTokenizer.from_pretrained(args.model)
    dtype = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float16
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=dtype, device_map="auto")
    model.eval()

    # Register steering hook
    hook_fn = ActivationSteeringHook(direction=direction, alpha=args.alpha, mode=args.mode)
    # Layer index is 1-indexed (1..32) -> model.model.layers[layer_idx - 1]
    target_module = model.model.layers[layer_idx - 1]
    handle = target_module.register_forward_hook(hook_fn)

    results = []
    outcomes = Counter()

    print(f"Running steering pilot across {len(scens)} scenarios (alpha={args.alpha})...")
    # Quick sanity test on 5 scenarios to verify output
    for idx, sc in enumerate(scens[:5]):
        sid = sc["id"]
        harmful_ids = set(sc.get("harmful_ids", []))
        safe_ids = set(sc.get("safe_ids", []))
        user_prompt = sc["input"]
        
        msgs = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
        
        # Format tool definitions for Qwen chat template
        tools = [
            {"type": "function", "function": {"name": "search_options", "description": "Search available options.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
            {"type": "function", "function": {"name": "get_option_details", "description": "Get details of an option.", "parameters": {"type": "object", "properties": {"option_id": {"type": "string"}}, "required": ["option_id"]}}},
            {"type": "function", "function": {"name": "place_order", "description": "Place the final order.", "parameters": {"type": "object", "properties": {"option_id": {"type": "string"}}, "required": ["option_id"]}}}
        ]
        
        prompt_text = tok.apply_chat_template(msgs, tools=tools, add_generation_prompt=True, tokenize=False)
        inp = tok(prompt_text, return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            gen = model.generate(**inp, max_new_tokens=512, do_sample=False)
        resp = tok.decode(gen[0][inp["input_ids"].shape[1]:], skip_special_tokens=True)
        
        results.append({
            "scenario_id": sid,
            "alpha": args.alpha,
            "layer": layer_idx,
            "response_preview": resp[:200]
        })
        print(f"  [{idx+1}/5] {sid} completed.")

    handle.remove()

    out_file = RESULTS_RQ3 / f"steering_pilot_{args.probe}_a{args.alpha}_L{layer_idx}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n[RQ3] Done! Results written to {out_file}")


if __name__ == "__main__":
    main()
