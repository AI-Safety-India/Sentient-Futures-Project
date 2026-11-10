"""Offline validation helpers for the versioned E2 pilot.

No inference, network, downloads, or automatic legacy-pipeline execution.
Missing evidence fails closed. Use reported status separately from authorization.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Iterable, Mapping


class ValidationBlocked(ValueError):
    """Required measurement evidence is absent, invalid, or failed."""


def ids_sha256(ids: Iterable[int]) -> str:
    values = list(ids)
    if any(type(value) is not int or value < 0 for value in values):
        raise ValueError("Token IDs must be nonnegative integers")
    return hashlib.sha256(json.dumps(values, separators=(",", ":")).encode()).hexdigest()


def measured_input_check(expected_ids, logged_count=None, actual_backend_ids=None):
    """Report only observed comparisons; count equality is not ID equality."""
    expected = list(expected_ids)
    ids_sha256(expected)
    if logged_count is not None and (type(logged_count) is not int or logged_count < 0):
        raise ValueError("logged_count must be a nonnegative integer")
    actual = list(actual_backend_ids) if actual_backend_ids is not None else None
    if actual is not None:
        ids_sha256(actual)
    exact = actual == expected if actual is not None else None
    first = None
    if exact is False:
        first = next((i for i, (a, b) in enumerate(zip(expected, actual)) if a != b), min(len(expected), len(actual)))
    return dict(expected_count=len(expected), logged_count=logged_count,
                count_matches=(len(expected) == logged_count if logged_count is not None else None),
                actual_backend_count=(len(actual) if actual is not None else None),
                token_ids_match=exact, first_mismatch=first,
                exact_input_verified=exact is True,
                expected_ids_sha256=ids_sha256(expected))


def select_layer_on_validation(rows: Iterable[Mapping], center_layer=20):
    """Max val AUROC, then val accuracy, then proximity to L20, then lower layer.

    The final lower-layer rule only resolves an otherwise exact tie. Test metrics
    are deliberately ignored. Every row must supply both validation metrics.
    """
    candidates = list(rows)
    if not candidates:
        raise ValidationBlocked("No layer candidates")
    layers = []
    for row in candidates:
        layer = row["layer"]
        if type(layer) is not int or layer < 1:
            raise ValidationBlocked("Layers must be positive one-based integers")
        layers.append(layer)
        for key in ("val_auroc", "val_accuracy"):
            value = row.get(key)
            if value is None or not math.isfinite(value) or not 0 <= value <= 1:
                raise ValidationBlocked(f"Missing or invalid {key}")
    if len(set(layers)) != len(layers):
        raise ValidationBlocked("Duplicate layers")
    return dict(max(candidates, key=lambda r: (r["val_auroc"], r["val_accuracy"],
                                               -abs(r["layer"]-center_layer), -r["layer"])))


IDENTITY_FIELDS = (
    "schema", "model_id", "model_revision", "template_sha256", "prompt_sha256",
    "input_ids_sha256", "input_token_count", "positions", "layers_one_based",
    "hidden_state_semantics", "dtype", "backend", "backend_versions",
)


def make_cache_identity(*, model_id, model_revision, template_sha256, prompt_text,
                        input_ids, positions, layers_one_based, dtype, backend,
                        backend_versions):
    """Describe the extraction to be compared to evidence from its producer."""
    ids = list(input_ids)
    if not ids:
        raise ValueError("Empty input")
    if not positions or any(type(p) is not int or p < 0 or p >= len(ids) for p in positions):
        raise ValueError("Invalid extraction positions")
    if not layers_one_based or any(type(l) is not int or l < 1 for l in layers_one_based):
        raise ValueError("Invalid one-based layers")
    if not all((model_id, model_revision, template_sha256, dtype, backend, backend_versions)):
        raise ValueError("Identity fields must be specified")
    return dict(schema="e2-pilot-cache-v1", model_id=model_id, model_revision=model_revision,
                template_sha256=template_sha256,
                prompt_sha256=hashlib.sha256(prompt_text.encode()).hexdigest(),
                input_ids_sha256=ids_sha256(ids), input_token_count=len(ids),
                positions=list(positions), layers_one_based=list(layers_one_based),
                hidden_state_semantics="post_decoder_layer_excludes_embeddings",
                dtype=dtype, backend=backend, backend_versions=dict(backend_versions))


def verify_cache(cache_path, manifest, expected_identity):
    """Verify identity and payload hash BEFORE loading an activation payload.

    Never create a producer manifest retrospectively from desired metadata: that
    would not establish historical provenance. Legacy caches without manifests
    remain unverified rather than being silently upgraded.
    """
    differences = [key for key in IDENTITY_FIELDS
                   if key not in manifest or key not in expected_identity
                   or manifest[key] != expected_identity[key]]
    if differences:
        raise ValidationBlocked("Cache identity mismatch/missing: " + ", ".join(differences))
    actual = hashlib.sha256(Path(cache_path).read_bytes()).hexdigest()
    if manifest.get("payload_sha256") != actual:
        raise ValidationBlocked("Cache payload hash mismatch or missing")
    return {"verified": True, "payload_sha256": actual}


REQUIRED_MEASUREMENT_GATES = (
    "human_labels_reviewed", "matched_context_and_metadata", "exact_runtime_input_ids",
    "cache_identity_verified", "heldout_product_groups_disjoint", "final_answer_checks",
    "e2_same_layer_nuisance_controls", "content_evaluation_separation",
    "silent_context_transfer", "fresh_frozen_validation",
)


def measurement_gate_report(evidence: Mapping):
    """Do not infer pass from numeric truthiness, completed jobs, or missing keys.

    Each gate expects {status: 'pass'|'fail'|'unresolved', evidence: <artifact> }.
    Numerical criteria belong in the frozen pilot protocol, not this generic
    helper. This gate is for the strong interpretation, not permission to run a
    clearly labelled development experiment.
    """
    blockers = []
    for key in REQUIRED_MEASUREMENT_GATES:
        row = evidence.get(key)
        if not isinstance(row, Mapping) or row.get("status") != "pass" or not row.get("evidence"):
            blockers.append(key)
    return dict(measurement_validated=not blockers, blockers=blockers,
                paid_execution_authorized=False, rq3_runtime_verified=False)


def require_measurement_gates(evidence):
    report = measurement_gate_report(evidence)
    if report["blockers"]:
        raise ValidationBlocked("Measurement gates unresolved/failed: " + ", ".join(report["blockers"]))
    return report
