"""RQ3 Causal Steering Harness for Qwen3.5-9B (`INTERP_PLAN.md` §6.5 & `results/rq3/RQ3_PREREGISTRATION.md`).

Tests whether injecting the evaluation probe vector (h <- h + alpha * w_eval)
into the residual stream during agent generation turns increases safe orders.

Usage:
    python domains/menu_planning/scripts/rq3/run_rq3_steering.py --alpha 1.0 --layer 26 --scenarios tuning
"""
import argparse
import csv
import json
import os
import random
import sys
from collections import Counter, defaultdict
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
        # Residual stream output can be a tensor or tuple where output[0] is the hidden state
        if isinstance(output, tuple):
            h = output[0]
            rest = output[1:]
        else:
            h = output
            rest = None

        if self.mode == "add":
            # Add alpha * direction
            h_mod = h + (self.alpha * self.direction.to(h.device, dtype=h.dtype))
        elif self.mode == "ablate":
            # Project out direction: h - (h . v) v
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

    print(f"=== Running RQ3 Causal Steering ===")
    print(f"Direction: {args.probe} | Layer: {layer_idx} | Alpha: {args.alpha} | Mode: {args.mode}")

    out_file = RESULTS_RQ3 / f"steering_results_{args.probe}_a{args.alpha}_L{layer_idx}.json"
    print(f"Target output: {out_file}")


if __name__ == "__main__":
    main()
