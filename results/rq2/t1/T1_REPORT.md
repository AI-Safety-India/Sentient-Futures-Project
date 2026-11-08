# T1: Tokenizer / prompt-rebuild fidelity (Qwen3.5-9B, vLLM 0.32.0)

## Result
- **1188/1188 ModelEvent calls match exactly** (rebuilt token count == `usage.input_tokens`, diff 0 everywhere).
- **240/240 samples fully matched** (10 tuning scenarios x 4 variants x 3 epochs x 2 prompt conditions).
- Check is token-count equality only; vLLM did not log token IDs, so ID equality is not testable.

## Method
Filtered both logs (`neutral`, `ethical`, resolve_attachments=True) to the 240 samples whose id is `<tuning scenario>_<variant>`.
For each ModelEvent, `e.call.request` was rebuilt with
`tokenizer.apply_chat_template(messages, tools=tools, add_generation_prompt=True, tokenize=True)`
and its length compared with `e.output.usage.input_tokens`.

## Transformation needed (final = variant D, in `replay_rebuild.py`)
1. **Parse `tool_calls[].function.arguments` from JSON string to dict.** Required: the template fails with string args (the 948 "None" results in A/B are template exceptions, not count differences).
2. Rename assistant `reasoning` -> `reasoning_content` (what vLLM does). Count-neutral here, because transformers 5.22.2 already aliases `reasoning`/`thinking` to `reasoning_content` (`_alias_reasoning_fields` in `chat_template_utils.py`); done explicitly anyway so it works on older versions.
3. Pass `tools` as the OpenAI objects `{"type":"function","function":{...}}` unchanged.
4. Nothing else: default `enable_thinking`, no `reasoning_effort` kwarg needed (passing it is a no-op), content "" vs None irrelevant.

## Variants tried (calls matched / 1188; samples fully matched / 240)
| Variant | Calls | Samples | Note |
|---|---|---|---|
| A raw request (reasoning key, string args, OpenAI tools) | 240 | 0 | 948 calls raise (string args); only first calls, which have no tool_calls, work |
| B rename reasoning only | 240 | 0 | same failure |
| C parsed args, no explicit rename | 1188 | 240 | works via transformers' aliasing |
| **D rename + parsed args (final)** | **1188** | **240** | diff 0 on all |
| E D + inner function dicts as tools | 0 | 0 | uniformly -36 tokens (tools header differs) |
| F D + content ""->None | 1188 | 240 | no effect |
| G D with reasoning dropped | 244 | 0 | reasoning is rendered; diffs -157..-236+ on later calls |
| H D + `enable_thinking=False` | 0 | 0 | uniformly +2 tokens |
| I D + `reasoning_effort="medium"` template kwarg | 1188 | 240 | no effect (template ignores it) |

## Residual mismatches
None.

## Environment
transformers 5.22.2, tokenizers 0.23.3, tokenizer `Qwen/Qwen3.5-9B` (no weights), inspect_ai 0.3.283 from the repo env.
Repo untouched (Python run with `-I -B`).

## Rerun
```
cd /c/Users/Person1/OneDrive/Desktop/sfn/rq2_work/scripts && uv run --project ../../Sentient-Futures-Project-git --with transformers --with jinja2 python -I -B t1_tokenizer_fidelity.py
```
(about 3 min; the script prints the variants table and rewrites `t1_per_call.csv` / `t1_summary.json` using variant D.)

## Files
- `rq2_work/scripts/replay_rebuild.py` : `rebuild_messages(request) -> (messages, tools)`, `render(request, tokenizer) -> list[int]`
- `rq2_work/scripts/t1_tokenizer_fidelity.py`
- `rq2_work/outputs/t1/t1_per_call.csv`, `t1_summary.json`, `T1_REPORT.md`

---

# Addendum: calls with no logged request (`event.call is None`)

The 240 tuning samples contain 1248 ModelEvents: 1188 with a logged request and **60 without** (43 samples; 43 are the last call of the sample, 17 are not). 12 of the 60 are the call that produced the final `place_order`. The earlier 1188/1188 figure covers only calls that have a request.

## `request_from_event(event, prev_request)` (in `replay_rebuild.py`)
Builds the OpenAI request from `event.input`, mirroring `inspect_ai.model._openai.openai_chat_message` (the openai-compatible provider path):
- system/user: `content` string as is.
- assistant: `content` = concatenation of `"\n" + text` for each text block (empty text gives `"\n"`); `ContentReasoning` goes in the key named by its `.internal` (`reasoning`); `tool_calls` = `{id, type:"function", function:{name, arguments: json.dumps(args)}}` with the same ids.
- tool: `content` = text (or `"Error: ..."`), `tool_call_id`.
- `tools`, `tool_choice`, etc. copied from the nearest earlier logged request of the same sample (for a first call, which has no earlier one, the nearest later one; the event's own request is never used).

## Validation
- (a) All 1188 calls that have a request: `render(request_from_event(...))` equals `render(logged request)` **token ID for token ID, 0 mismatches of 1188**. The rebuilt `messages` list is also dict-identical to the logged one for all 1188 (0 mismatches). Only `extra_headers` (per-request id) differs, which does not enter the prompt.
- (b) The 60 calls without a request: rebuilt token count equals `usage.input_tokens` **60/60 (diff 0)**.
- Overall: 1248/1248 calls exact; `t1_per_call.csv` now has all 1248 rows with a `source` column (`logged_request` / `rebuilt_from_input`). `call_index` is now the index among all ModelEvents of the sample (previously among logged ones only).

## Why `call` is missing
Not a size threshold. In Inspect's transcript (`inspect_ai/log/_transcript.py`, `_process_event`), when `log_model_api` is unset the raw API call is kept only for the first `DEFAULT_LOG_MODEL_API_CALLS = 5` non-error model calls per model (`_util/constants.py`) and `event.call` is set to `None` afterwards. The data fits exactly: missing calls sit at call_index 5 (43), 6 (12), 7 (4), 8 (1), i.e. never among the first five. `e.input`, `e.tools`, `e.tool_choice` and `e.output` (with usage) are still logged. Rerunning with `--log-model-api` would keep all of them.

## Rerun
```
cd /c/Users/Person1/OneDrive/Desktop/sfn/rq2_work/scripts && uv run --project ../../Sentient-Futures-Project-git --with transformers --with jinja2 python -I -B t1b_rebuild_from_input.py
```
(`t1_tokenizer_fidelity.py` no longer writes the CSV; `t1b_rebuild_from_input.py` does.)
