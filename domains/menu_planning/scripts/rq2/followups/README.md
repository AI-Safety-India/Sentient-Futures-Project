# Scientific source for the RQ2 follow-ups

This folder preserves the scientific builders, extractors, analysis kernels, tests and frozen design records used for the follow-up studies. It excludes notebook pairing clients, credentials, upload chunks, download clients and runtime logs. Copied source files are byte-identical to their local originals; `publication_manifest.json` records their paths and digests.

Read `results/rq2/FOLLOWUP_INDEX.md` from the repository root for the results and interpretation. Original result files are unchanged. The small selected-state NPZ files under the versioned results folders support local numerical work; full remote caches and the historical training cache are not supplied here.

## How to use this archive

- Pure analysis functions and synthetic unit tests can run locally with the dependencies they import, principally NumPy. They do not need a model or GPU.
- The historical scripts are preserved, not silently rewritten into a new experiment. Some launchers and analysis entry points refer to the original workspace layout, Windows absolute paths, `/marimo`, external caches or recorded path hashes. They are not a turnkey portable rerun command. Adapt paths only in a new working copy, retain the original bytes and hashes, and write outputs to a new directory.
- Frozen job JSONs include exact input records. A filename containing `draft` can be the frozen file actually consumed in v8; its execution manifest and SHA-256 identify the executed version.
- `fresh_validation_*` files are prospective examples, not completed model results. Do not merge them with the inspected eight-pair development results.
- Producer/extractor files import model libraries and can perform inference when explicitly run. No model execution is part of the local verification commands below. Any later compute must be explicitly confirmed free; this archive does not authorise charges.

## Local regression checks

From the repository root, using an existing Python environment with NumPy:

```text
python -m unittest discover -s domains/menu_planning/scripts/rq2 -p "test_*.py"
python -m unittest discover -s domains/menu_planning/scripts/rq2/followups/e2_scoring_v9 -p "test_score_fit.py"
python -m unittest discover -s domains/menu_planning/scripts/rq2/followups/e2_training_design_v8 -p "test_analyze_v8.py"
```

These commands test input preservation, exact backend token checks, first-reading selection, AUROC handling, synthetic scorer behaviour and v8 provenance checks. They do not run `run_local.py`, regenerate results or start model passes.

The repaired benchmark analysis lives in the parent `repair_analysis.py`; the input contract in `input_contract.py` rejects mismatched actual backend IDs and preserves logged reasoning. `complete_t6_and_build_splits.py` no longer invents human pass labels, and the G5/R2 entry point writes a separate repair analysis instead of overwriting the original reports. Legacy training/extraction entry points are not a protected archival replay route and should not be run against preserved outputs.
