def run_rq2_targeted_repair():
    import copy
    import gc
    import gzip
    import hashlib
    import importlib.metadata
    import importlib.util
    import inspect
    import json
    import re
    import subprocess
    import sys
    import zipfile
    from collections import defaultdict
    from pathlib import Path

    try:
        import zipfile_zstd
    except ModuleNotFoundError:
        print("Installing the small ZIP-reading dependency...", flush=True)
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "zipfile-zstd"],
            check=True,
            capture_output=True,
            text=True,
        )
        importlib.invalidate_caches()
        import zipfile_zstd

    import numpy as np
    import torch
    import transformers
    from huggingface_hub import hf_hub_download
    from transformers import AutoConfig, AutoTokenizer

    REPO = Path("/home/marimo/Sentient-Futures-Project")
    DATA = REPO / "results/rq2"
    CACHE = Path("/home/marimo/rq2_work/outputs/g4/npz")
    OUTPUT = Path.cwd() / "rq2_targeted_repair_v1"
    ARCHIVE = Path.cwd() / "rq2_targeted_repair_v1.zip"
    MODEL_ID = "Qwen/Qwen3.5-9B"
    REVISION = "c202236235762e1c871ad0ccb60c8ee5ba337b9a"

    print("RQ2 TARGETED REPAIR — restored-session version", flush=True)

    if ARCHIVE.exists():
        print("A completed export already exists:")
        print(ARCHIVE)
        print("Download it through Files. No further run is needed.")
        return

    if not torch.cuda.is_available():
        print("STOP: attach a GPU in Molab, then run this cell again.")
        return

    print("GPU:", torch.cuda.get_device_name(0), flush=True)

    audit_path = next(
        (
            p for p in (
                Path.cwd() / "rq2_all_runs_cpu_audit.json.gz",
                Path("/marimo/rq2_all_runs_cpu_audit.json.gz"),
                Path("/home/marimo/rq2_all_runs_cpu_audit.json.gz"),
            )
            if p.exists()
        ),
        None,
    )
    if audit_path is None:
        raise FileNotFoundError("Run the recovery ZIP extraction cell first.")

    positions_path = DATA / "t2/qwen35_positions_1200.jsonl"
    helper_path = (
        REPO / "domains/menu_planning/scripts/rq2/replay_rebuild.py"
    )
    for path in (positions_path, helper_path):
        if not path.exists():
            raise FileNotFoundError(f"Restored input missing: {path}")

    with gzip.open(audit_path, "rt", encoding="utf-8") as f:
        audit = json.load(f)

    if (
        audit["summary"]["completed_runs"] != 1200
        or audit["summary"]["errors"] != 0
    ):
        raise RuntimeError("The CPU audit is incomplete or has errors.")

    def sha(value):
        return hashlib.sha256(value).hexdigest()

    if sha(positions_path.read_bytes()) != audit["input_hashes"]["positions"]:
        raise RuntimeError("Position file differs from the audited version.")
    if sha(helper_path.read_bytes()) != audit["input_hashes"]["replay_helper"]:
        raise RuntimeError("Replay helper differs from the audited version.")

    records = {
        r["run_id"]: r
        for r in (
            json.loads(line)
            for line in positions_path.read_text().splitlines()
            if line.strip()
        )
    }
    audited = {r["run_id"]: r for r in audit["runs"]}

    spec = importlib.util.spec_from_file_location(
        "rq2_existing_rebuild", helper_path
    )
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)

    # Read the saved log format without needing Inspect installed.
    def expand(value, attachments):
        if isinstance(value, str) and value.startswith("attachment://"):
            return expand(
                attachments[value.split("://", 1)[1]], attachments
            )
        if isinstance(value, list):
            return [expand(v, attachments) for v in value]
        if isinstance(value, dict):
            return {k: expand(v, attachments) for k, v in value.items()}
        return value

    def resolve_ranges(pool, ranges):
        result = []
        for start, stop in ranges:
            if not 0 <= start <= stop <= len(pool):
                raise ValueError("Invalid log reference")
            result.extend(pool[start:stop])
        return result

    def assistant_message(message):
        content = message.get("content", "")
        extra = {}
        if not isinstance(content, str):
            text = ""
            for block in content or []:
                if block["type"] == "reasoning":
                    key = str(block.get("internal"))
                    if key not in (
                        "reasoning", "reasoning_content", "reasoning_details"
                    ):
                        raise ValueError("Unsupported reasoning format")
                    extra[key] = block["reasoning"]
                elif block["type"] == "text":
                    text += "\n" + block["text"]
                else:
                    raise ValueError("Unsupported assistant content")
            content = text

        result = {"role": "assistant", "content": content, **extra}
        if message.get("tool_calls"):
            result["tool_calls"] = [
                {
                    "id": t["id"],
                    "type": "function",
                    "function": {
                        "name": t["function"],
                        "arguments": json.dumps(t["arguments"]),
                    },
                }
                for t in message["tool_calls"]
            ]
        return result

    def read_requests(sample):
        sample = expand(sample, sample.get("attachments", {}))
        events = [e for e in sample["events"] if e["event"] == "model"]
        pools = sample.get("events_data", {})
        result = []

        for event in events:
            call = event.get("call")
            if call:
                request = copy.deepcopy(call["request"])
                if call.get("call_refs") is not None:
                    if call.get("call_key") != "messages":
                        raise ValueError("Unexpected call-reference format")
                    request["messages"] = resolve_ranges(
                        pools["calls"], call["call_refs"]
                    )
                source = "logged_request"
            else:
                donor = next(
                    e["call"]["request"] for e in events if e.get("call")
                )
                request = {
                    k: copy.deepcopy(v)
                    for k, v in donor.items() if k != "messages"
                }
                inputs = (
                    resolve_ranges(pools["messages"], event["input_refs"])
                    if event.get("input_refs") is not None
                    else event["input"]
                )
                messages = []
                for message in inputs:
                    role = message["role"]
                    if role == "assistant":
                        messages.append(assistant_message(message))
                        continue
                    if role not in ("system", "user", "tool"):
                        raise ValueError(f"Unsupported role: {role}")
                    content = message.get("content", "")
                    if not isinstance(content, str):
                        raise ValueError("Unsupported non-text input")
                    if role == "tool" and message.get("error"):
                        content = "Error: " + message["error"]["message"]
                    item = {"role": role, "content": content}
                    if role == "tool":
                        item["tool_call_id"] = str(message["tool_call_id"])
                    messages.append(item)
                request["messages"] = messages
                source = "reconstructed_request"

            if not request.get("messages"):
                raise ValueError("Empty request")
            result.append((event, request, source))
        return result

    # Prefer cached files; recover missing required files if necessary.
    print("Loading pinned tokenizer and configuration...", flush=True)

    def load_pinned(loader):
        try:
            return loader(local_files_only=True)
        except OSError:
            print(
                "Required model files are missing locally; "
                "fetching the pinned revision...",
                flush=True,
            )
            return loader(local_files_only=False)

    config_file = load_pinned(
        lambda **kw: hf_hub_download(
            repo_id=MODEL_ID,
            filename="config.json",
            revision=REVISION,
            **kw,
        )
    )
    tokenizer = load_pinned(
        lambda **kw: AutoTokenizer.from_pretrained(
            MODEL_ID, revision=REVISION, **kw
        )
    )
    config = AutoConfig.from_pretrained(
        str(Path(config_file).parent), local_files_only=True
    )

    template_hash = sha(str(tokenizer.chat_template).encode())
    if template_hash != audit["input_hashes"]["chat_template"]:
        raise RuntimeError("Tokenizer template differs from the audited one.")

    text_config = getattr(config, "text_config", config)
    if (
        getattr(text_config, "num_hidden_layers", None) != 32
        or getattr(text_config, "hidden_size", None) != 4096
    ):
        raise RuntimeError("Expected a model with 32 layers and width 4096.")

    def render(request, generation_prompt):
        messages, tools = helper.rebuild_messages(request)
        text = tokenizer.apply_chat_template(
            messages, tools=tools, tokenize=False,
            add_generation_prompt=generation_prompt,
        )
        encoded = tokenizer(
            text, add_special_tokens=False,
            return_offsets_mapping=True,
        )
        ids = list(encoded["input_ids"])
        direct = tokenizer.apply_chat_template(
            messages, tools=tools, tokenize=True,
            add_generation_prompt=generation_prompt,
        )
        if hasattr(direct, "keys"):
            direct = direct["input_ids"]
        if ids != list(direct):
            raise RuntimeError("Direct and offset tokenization disagree.")
        return text, ids, encoded["offset_mapping"]

    def token_at(offsets, character):
        for index, (start, stop) in enumerate(offsets):
            if start <= character < stop:
                return index
        raise ValueError(f"Cannot map character {character} to a token")

    option_pattern = re.compile(
        r"<tool_response>\n"
        r"(Option Details:\n\s+Name: .*?\n\s+ID: ([^\n]+)\n.*?)"
        r"\n(</tool_response>)",
        re.DOTALL,
    )

    def detail_messages(request):
        return [
            m for m in request["messages"]
            if m["role"] == "tool"
            and isinstance(m.get("content"), str)
            and "Option Details:\n" in m["content"]
        ]

    def option_id(message):
        match = re.search(r"\n\s+ID: ([^\n]+)", message["content"])
        if match is None:
            raise ValueError("Missing option ID")
        return match.group(1).strip()

    prefix_flagged = {
        r["run_id"] for r in audit["runs"]
        if any(not c["matches_final_prefix"] for c in r["calls"])
    }
    index_flagged = {
        r["run_id"] for r in audit["runs"]
        if any(c["index_name"] == "tok_idx" for c in r["index_changes"])
    }
    wanted = prefix_flagged | index_flagged
    jobs = []
    repaired_runs = set()
    diagnostic_runs = set()

    print("Preparing the targeted extraction plan...", flush=True)

    for condition in ("neutral", "ethical"):
        logs = list(
            (REPO / "results/logs/full/qwen3.5-9b" / condition).glob("*.eval")
        )
        if len(logs) != 1:
            raise RuntimeError(f"Expected one {condition} log")

        with zipfile.ZipFile(logs[0]) as archive:
            for filename in archive.namelist():
                if not (
                    filename.startswith("samples/")
                    and filename.endswith(".json")
                ):
                    continue

                sample = json.loads(archive.read(filename))
                run_id = (
                    f"{condition}__{sample['id']}__ep{int(sample['epoch'])}"
                )
                if run_id not in wanted:
                    continue

                record = records[run_id]
                checked = audited[run_id]
                calls = read_requests(sample)
                target = record["target_call_idx"]
                reads = detail_messages(calls[target][1])

                if [option_id(m) for m in reads] != [
                    p["option_id"] for p in record["pos_a"]
                ]:
                    raise RuntimeError(f"Reading identities changed: {run_id}")

                original_calls = []
                for message in reads:
                    tool_id = message["tool_call_id"]
                    original_calls.append(next(
                        i for i, (_, request, _) in enumerate(calls)
                        if any(
                            m.get("tool_call_id") == tool_id
                            for m in request["messages"]
                            if m["role"] == "tool"
                        )
                    ))

                by_call = defaultdict(list)

                if run_id in prefix_flagged:
                    for i, position in enumerate(record["pos_a"]):
                        ci = original_calls[i]
                        if not checked["calls"][ci]["matches_final_prefix"]:
                            by_call[ci].append({
                                "kind": "pos_a",
                                "sub_idx": position["sub_idx"],
                                "old_cache_row": i,
                                "tool_call_id": reads[i]["tool_call_id"],
                                "option_id": position["option_id"],
                            })

                    for position in record["pos_b"]:
                        earlier = [
                            i for i, p in enumerate(record["pos_a"])
                            if p["tok_idx"] < position["tok_idx"]
                        ]
                        if not earlier:
                            raise RuntimeError("Persistence mapping failed")
                        last = earlier[-1]
                        if option_id(reads[last]) != position["last_option_id"]:
                            raise RuntimeError("Persistence identity mismatch")

                        ci = original_calls[last]
                        if not checked["calls"][ci]["matches_final_prefix"]:
                            by_call[ci].append({
                                "kind": "pos_b",
                                "sub_idx": position["sub_idx"],
                                "old_cache_row": (
                                    len(record["pos_a"]) + position["sub_idx"]
                                ),
                                "tool_call_id": reads[last]["tool_call_id"],
                            })

                for ci, metadata in sorted(by_call.items()):
                    event, request, source = calls[ci]
                    text, ids, offsets = render(request, True)
                    if len(ids) != event["output"]["usage"]["input_tokens"]:
                        raise RuntimeError(
                            f"Original-call token count differs: {run_id}, {ci}"
                        )

                    original_reads = detail_messages(request)
                    matches = list(option_pattern.finditer(text))
                    if [option_id(m) for m in original_reads] != [
                        m.group(2).strip() for m in matches
                    ]:
                        raise RuntimeError("Tool-response matching failed")

                    indices = []
                    for item in metadata:
                        if item["kind"] == "pos_a":
                            occurrence = next(
                                i for i, m in enumerate(original_reads)
                                if m["tool_call_id"] == item["tool_call_id"]
                            )
                            index = token_at(
                                offsets, matches[occurrence].start(3)
                            )
                        else:
                            if not text.endswith("<think>\n"):
                                raise RuntimeError(
                                    "Unexpected assistant generation boundary"
                                )
                            index = token_at(offsets, len(text) - 1)

                        item["new_token_index"] = index
                        item["new_token"] = tokenizer.decode([ids[index]])
                        indices.append(index)

                    jobs.append({
                        "kind": "replacement",
                        "run_id": run_id,
                        "call_index": ci,
                        "request_source": source,
                        "input_ids": ids,
                        "indices": indices,
                        "positions": metadata,
                    })
                    repaired_runs.add(run_id)

                if run_id in index_flagged:
                    if not (CACHE / f"{run_id}.npz").exists():
                        raise FileNotFoundError(
                            f"Diagnostic cache missing: {run_id}"
                        )

                    event, request, source = calls[target]
                    full_request = dict(
                        request,
                        messages=request["messages"] + [
                            assistant_message(
                                event["output"]["choices"][0]["message"]
                            )
                        ],
                    )
                    _, ids, _ = render(full_request, False)
                    if len(ids) != checked["direct_length"]:
                        raise RuntimeError("Diagnostic reconstruction changed")

                    old_positions = (
                        [p["tok_idx"] for p in record["pos_a"]]
                        + [p["tok_idx"] for p in record["pos_b"]]
                        + (
                            [record["pos_c"]["tok_idx"]]
                            if record["pos_c"] is not None else []
                        )
                    )
                    corrected = list(old_positions)
                    changes = []

                    for change in checked["index_changes"]:
                        if change["index_name"] != "tok_idx":
                            continue
                        if not change["applicable_to_direct_ids"]:
                            raise RuntimeError("Unresolved index mapping")

                        if change["kind"] == "pos_a":
                            row = change["position"]
                        elif change["kind"] == "pos_b":
                            row = len(record["pos_a"]) + change["position"]
                        else:
                            row = len(record["pos_a"]) + len(record["pos_b"])

                        if old_positions[row] != change["stored_index"]:
                            raise RuntimeError("Stored diagnostic index changed")

                        new = change["recomputed_offset_index"]
                        if tokenizer.decode([ids[new]]) != (
                            change["recomputed_offset_window"]["token"]
                        ):
                            raise RuntimeError("Corrected token changed")

                        corrected[row] = new
                        changes.append({
                            "old_cache_row": row,
                            "kind": change["kind"],
                            "stored_index": old_positions[row],
                            "corrected_index": new,
                        })

                    jobs.append({
                        "kind": "diagnostic",
                        "run_id": run_id,
                        "call_index": target,
                        "request_source": source,
                        "input_ids": ids,
                        "indices": sorted(set(old_positions + corrected)),
                        "old_positions": old_positions,
                        "corrected_positions": corrected,
                        "changes": changes,
                    })
                    diagnostic_runs.add(run_id)

    replacement_jobs = [j for j in jobs if j["kind"] == "replacement"]
    if not (
        len(repaired_runs) == 20
        and len(replacement_jobs) == 21
        and sum(len(j["indices"]) for j in replacement_jobs) == 75
        and len(diagnostic_runs) == 3
        and len(jobs) == 24
    ):
        raise RuntimeError(
            "Plan does not match the reviewed 20 repairs and 3 diagnostics."
        )

    jobs.sort(key=lambda j: (
        0 if j["kind"] == "diagnostic" else 1,
        j["run_id"], j["call_index"],
    ))
    print(
        "Plan verified: 75 replacement snapshots, "
        "21 original-call forwards, 3 diagnostic forwards.",
        flush=True,
    )

    dtype = (
        torch.bfloat16
        if torch.cuda.is_bf16_supported() else torch.float16
    )
    architectures = getattr(config, "architectures", None) or []
    model_class = (
        getattr(transformers, architectures[0], None)
        if architectures else None
    )
    if model_class is None:
        raise RuntimeError(
            f"Unsupported installed model architecture: {architectures}"
        )

    OUTPUT.mkdir(exist_ok=True)
    print(
        f"Loading {architectures[0]} using {dtype}...",
        flush=True,
    )

    model = load_pinned(
        lambda **kw: model_class.from_pretrained(
            MODEL_ID,
            revision=REVISION,
            torch_dtype=dtype,
            device_map={"": 0},
            **kw,
        )
    )
    model.eval()
    model.requires_grad_(False)

    environment = {
        "model_id": MODEL_ID,
        "snapshot_revision": REVISION,
        "historical_revision_verified": False,
        "model_class": type(model).__name__,
        "dtype": str(dtype),
        "attention_implementation": str(
            getattr(
                getattr(model.config, "text_config", model.config),
                "_attn_implementation", None,
            )
        ),
        "config_sha256": sha(Path(config_file).read_bytes()),
        "template_sha256": template_hash,
        "audit_sha256": sha(audit_path.read_bytes()),
        "versions": {
            p: importlib.metadata.version(p)
            for p in ("torch", "transformers", "numpy")
        },
    }
    report = {
        "status": "running",
        "environment": environment,
        "replacement_runs": sorted(repaired_runs),
        "diagnostic_runs": sorted(diagnostic_runs),
        "completed_jobs": [],
        "diagnostic_comparisons": [],
        "interpretation": (
            "Candidate replacement states; original caches unchanged. "
            "Diagnostic review and score recomputation remain necessary."
        ),
    }

    def save_report():
        temporary = OUTPUT / "report.partial.json"
        temporary.write_text(
            json.dumps(report, indent=2), encoding="utf-8"
        )
        temporary.replace(OUTPUT / "report.json")

    def extract(ids, indices):
        device = model.get_input_embeddings().weight.device
        inputs = torch.tensor([ids], dtype=torch.long, device=device)
        kwargs = {
            "input_ids": inputs,
            "output_hidden_states": True,
            "use_cache": False,
            "return_dict": True,
        }
        if "logits_to_keep" in inspect.signature(model.forward).parameters:
            kwargs["logits_to_keep"] = 1

        with torch.inference_mode():
            result = model(**kwargs)

        hidden = getattr(result, "hidden_states", None)
        if hidden is None or len(hidden) != 33:
            raise RuntimeError(
                "Expected embeddings plus 32 hidden-state outputs."
            )

        states = np.stack(
            [
                layer[0, indices, :].to(torch.float16).cpu().numpy()
                for layer in hidden[1:]
            ],
            axis=1,
        )
        if states.shape != (len(indices), 32, 4096):
            raise RuntimeError(f"Unexpected state shape: {states.shape}")
        if not np.isfinite(states).all():
            raise RuntimeError("Non-finite activations")

        del result, hidden, inputs
        gc.collect()
        torch.cuda.empty_cache()
        return states

    def compare_layers(saved, current):
        a = np.asarray(saved, dtype=np.float64)
        b = np.asarray(current, dtype=np.float64)
        norms = np.linalg.norm(a, axis=-1)
        difference = a - b
        return {
            "relative_l2_error_by_layer": (
                np.linalg.norm(difference, axis=-1)
                / np.maximum(norms, 1e-12)
            ).tolist(),
            "cosine_by_layer": (
                np.sum(a * b, axis=-1)
                / np.maximum(
                    norms * np.linalg.norm(b, axis=-1), 1e-12
                )
            ).tolist(),
            "max_absolute_error": float(np.max(np.abs(difference))),
        }

    try:
        for number, job in enumerate(jobs, 1):
            filename = (
                f"{job['kind']}__{job['run_id']}"
                f"__call{job['call_index']}.npz"
            )
            destination = OUTPUT / filename
            signature = sha(json.dumps(
                {"environment": environment, "job": job},
                sort_keys=True,
            ).encode())

            if destination.exists():
                with np.load(destination, allow_pickle=False) as saved:
                    if str(saved["signature"].item()) != signature:
                        raise RuntimeError(
                            f"Existing output uses different settings: {filename}"
                        )
                    states = saved["hidden_states"].copy()
                if (
                    states.shape != (len(job["indices"]), 32, 4096)
                    or not np.isfinite(states).all()
                ):
                    raise RuntimeError(f"Invalid existing output: {filename}")
                print(f"Reusing completed job {number}/24", flush=True)
            else:
                print(
                    f"Running {number}/24: {job['kind']} "
                    f"{job['run_id']} call {job['call_index']}",
                    flush=True,
                )
                states = extract(job["input_ids"], job["indices"])
                temporary = destination.with_suffix(".partial.npz")
                np.savez_compressed(
                    temporary,
                    hidden_states=states,
                    token_indices=np.asarray(job["indices"], dtype=np.int64),
                    input_ids=np.asarray(job["input_ids"], dtype=np.int64),
                    signature=np.asarray(signature),
                )
                temporary.replace(destination)

            metadata = {
                k: v for k, v in job.items() if k != "input_ids"
            }
            metadata["file"] = filename
            metadata["signature"] = signature
            metadata["input_ids_sha256"] = sha(
                np.asarray(job["input_ids"], dtype=np.int64).tobytes()
            )
            report["completed_jobs"].append(metadata)

            if job["kind"] == "diagnostic":
                with np.load(
                    CACHE / f"{job['run_id']}.npz",
                    allow_pickle=False,
                ) as saved:
                    original = saved["hidden_states"]

                if original.shape != (
                    len(job["old_positions"]), 32, 4096
                ):
                    raise RuntimeError("Original diagnostic cache shape differs")

                lookup = {
                    token: row for row, token in enumerate(job["indices"])
                }
                comparisons = []
                for row, (old, corrected) in enumerate(zip(
                    job["old_positions"], job["corrected_positions"]
                )):
                    comparisons.append({
                        "old_cache_row": row,
                        "stored_index": old,
                        "corrected_index": corrected,
                        "position_changed": old != corrected,
                        "old_cache_vs_current_stored_index": compare_layers(
                            original[row], states[lookup[old]]
                        ),
                        "old_cache_vs_current_corrected_index": compare_layers(
                            original[row], states[lookup[corrected]]
                        ),
                    })
                report["diagnostic_comparisons"].append({
                    "run_id": job["run_id"],
                    "rows": comparisons,
                })

            save_report()
            del states

        report["status"] = (
            "Extraction complete; diagnostic review and "
            "local score recomputation still required."
        )
        report["summary"] = {
            "replacement_runs": 20,
            "replacement_snapshots": 75,
            "replacement_forward_passes": 21,
            "diagnostic_runs": 3,
            "completed_jobs": len(report["completed_jobs"]),
            "original_caches_modified": False,
            "probe_scores_recomputed": False,
        }
        save_report()

        temporary_archive = ARCHIVE.with_suffix(".partial.zip")
        with zipfile.ZipFile(
            temporary_archive, "w", compression=zipfile.ZIP_STORED
        ) as bundle:
            bundle.write(OUTPUT / "report.json", arcname="report.json")
            for job in report["completed_jobs"]:
                bundle.write(OUTPUT / job["file"], arcname=job["file"])
        temporary_archive.replace(ARCHIVE)

        print("\n=== FINISHED ===")
        print(json.dumps(report["summary"], indent=2))
        print("\nDownload through the Files sidebar:")
        print(ARCHIVE)
        print(f"Archive size: {ARCHIVE.stat().st_size / 1e6:.1f} MB")

    except Exception as error:
        report["status"] = "stopped"
        report["error"] = f"{type(error).__name__}: {error}"
        save_report()
        print("\nSTOPPED:", report["error"])
        print("Completed outputs are saved. Original caches are unchanged.")
        raise

    finally:
        del model
        gc.collect()
        torch.cuda.empty_cache()


run_rq2_targeted_repair()