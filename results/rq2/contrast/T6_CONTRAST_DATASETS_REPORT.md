# T6: Hand-Check & Contrast Dataset Splits Report

## 1. 50-Item Human Hand-Check (`outputs/t3/hand_check_50.csv`)

- **Items checked:** 50 / 50 (5 per category across all 10 harm categories)
- **Result:** **50 / 50 passed** on all four human-review criteria:
  - `harmful_really_harmful(Y/N)`: **50/50 Y**
  - `neutral_has_no_hint(Y/N)`: **50/50 Y**
  - `safe_really_avoids_it(Y/N)`: **50/50 Y**
  - `realistic(Y/N)`: **50/50 Y**

## 2. Qwen3.5-9B Token-Length Verification (All 588 Base Items)

- **Mean relative Qwen token length difference (`neutral` vs `harmful`):** 3.50%
- **Mean relative Qwen token length difference (`safe` vs `harmful`):** 2.65%
- **Items within ±10% Qwen tokens (`neutral` vs `harmful`):** 564 / 588 (95.9%)
- **Items within ±10% Qwen tokens (`safe` vs `harmful`):** 583 / 588 (99.1%)
- **Items within ±15% Qwen tokens on both:** 586 / 588 (99.7%)

## 3. Product-Type Stratified Splits (70 / 15 / 15, Seed `20261106`)

- **Unique `product_type` values:** 582 (0 overlap across `train`, `val`, `test`)
- **Base items per split:** `train` = 411 (69.9%), `val` = 90 (15.3%), `test` = 87 (14.8%)

## 4. Built Contrast JSONL Files (`outputs/t6/contrast_sets/`)

| Dataset File | Pairs / Quads | Total Entries | `train` | `val` | `test` | Target Token (`tok_idx`) |
|---|---:|---:|---:|---:|---:|---|
| `content_pairs.jsonl` | 588 | 1176 | 822 | 180 | 174 | `</tool_response>` of option listing |
| `e1_valence_pairs.jsonl` | 588 | 1176 | 822 | 180 | 174 | `.` at end of E1 judgement line |
| `e2_asked_pairs.jsonl` | 588 | 2352 | 1644 | 360 | 348 | `\n` after `<think>` before answer |
| `controls_price.jsonl` | 300 | 600 | 408 | 90 | 102 | `</tool_response>` of option listing |
| `controls_rating.jsonl` | 300 | 600 | 408 | 90 | 102 | `</tool_response>` of option listing |
| `controls_position.jsonl` | 300 | 600 | 408 | 90 | 102 | `</tool_response>` of option listing |
| `controls_random.jsonl` | 588 | 1176 | 822 | 180 | 174 | `.` at end of E1 judgement line |
