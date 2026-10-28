# Run note: claude-opus-5

These pilot logs were run with **`strict_tools=false`, the default**. The tool definitions the model saw are identical to the original code on `main`.

The run used the local code version that contains the `strict_tools` switch, so the log metadata shows `strict_tools: false`. That version and the reason for the switch are in `results/logs/pilot/gpt-6-luna/CHANGES.md`. The switch is only turned on for OpenAI GPT-6 models.

Command used (the ethical run is identical except for `@menu_planning_welfare` and `<this folder>/ethical`):
```
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning   --model openrouter/anthropic/claude-opus-5 -M 'provider={data_collection: deny}'   -T categories=killing_slaughter_method   --epochs 1 --max-connections 2 --retry-on-error 5 --log-dir <this folder>/neutral
```
Pilot scope: category `killing_slaughter_method` = 5 scenarios × 4 variants × 1 epoch = **20 samples per condition**.
