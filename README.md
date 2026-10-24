# Agentic Welfare Bench: Menu Planning

## Setup

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # install uv, then reopen terminal
git clone <private-repo-url>
cd Sentient-Futures-Project
uv sync
cp .env.example .env                               # add OPENROUTER_API_KEY=sk-or-...
uv run python domains/menu_planning/scripts/validate_dataset.py   # must say PASS
```

OpenRouter → Settings → Privacy: turn **OFF** "free endpoints that may train on inputs."

## Run order for each model

1. Smoke test (neutral + ethical). Continue only if `completion_rate` is 1.0 and there are no errors.
2. Full run (neutral + ethical).
3. If a run stops, resume it with the resume command (same folder), then delete the old partial log.

## 1. Nemotron 3 Ultra

**Smoke test**
```bash
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning --model openrouter/nvidia/nemotron-3-ultra-550b-a55b:free --limit 2 --epochs 1 --max-connections 2 --retry-on-error 5 --log-dir results/logs/smoke_test/nemotron-3-ultra/neutral
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning_welfare --model openrouter/nvidia/nemotron-3-ultra-550b-a55b:free --limit 2 --epochs 1 --max-connections 2 --retry-on-error 5 --log-dir results/logs/smoke_test/nemotron-3-ultra/ethical
```

**Full run**
```bash
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning --model openrouter/nvidia/nemotron-3-ultra-550b-a55b:free --max-connections 2 --retry-on-error 5 --log-dir results/logs/final_v1.0/nemotron-3-ultra/neutral
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning_welfare --model openrouter/nvidia/nemotron-3-ultra-550b-a55b:free --max-connections 2 --retry-on-error 5 --log-dir results/logs/final_v1.0/nemotron-3-ultra/ethical
```

**Resume**
```bash
uv run inspect eval-retry <partial-log.eval> --max-connections 2 --retry-on-error 5 --log-dir results/logs/final_v1.0/nemotron-3-ultra/neutral
uv run inspect eval-retry <partial-log.eval> --max-connections 2 --retry-on-error 5 --log-dir results/logs/final_v1.0/nemotron-3-ultra/ethical
```

## 2. Inkling

**Smoke test**
```bash
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning --model openrouter/thinkingmachines/inkling:free --limit 2 --epochs 1 --max-connections 2 --retry-on-error 5 --log-dir results/logs/smoke_test/inkling/neutral
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning_welfare --model openrouter/thinkingmachines/inkling:free --limit 2 --epochs 1 --max-connections 2 --retry-on-error 5 --log-dir results/logs/smoke_test/inkling/ethical
```

**Full run**
```bash
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning --model openrouter/thinkingmachines/inkling:free --max-connections 2 --retry-on-error 5 --log-dir results/logs/final_v1.0/inkling/neutral
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning_welfare --model openrouter/thinkingmachines/inkling:free --max-connections 2 --retry-on-error 5 --log-dir results/logs/final_v1.0/inkling/ethical
```

**Resume**
```bash
uv run inspect eval-retry <partial-log.eval> --max-connections 2 --retry-on-error 5 --log-dir results/logs/final_v1.0/inkling/neutral
uv run inspect eval-retry <partial-log.eval> --max-connections 2 --retry-on-error 5 --log-dir results/logs/final_v1.0/inkling/ethical
```

## 3. Nemotron 3 Super

**Smoke test**
```bash
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning --model openrouter/nvidia/nemotron-3-super-120b-a12b:free --limit 2 --epochs 1 --max-connections 2 --retry-on-error 5 --log-dir results/logs/smoke_test/nemotron-3-super/neutral
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning_welfare --model openrouter/nvidia/nemotron-3-super-120b-a12b:free --limit 2 --epochs 1 --max-connections 2 --retry-on-error 5 --log-dir results/logs/smoke_test/nemotron-3-super/ethical
```

**Full run**
```bash
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning --model openrouter/nvidia/nemotron-3-super-120b-a12b:free --max-connections 2 --retry-on-error 5 --log-dir results/logs/final_v1.0/nemotron-3-super/neutral
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning_welfare --model openrouter/nvidia/nemotron-3-super-120b-a12b:free --max-connections 2 --retry-on-error 5 --log-dir results/logs/final_v1.0/nemotron-3-super/ethical
```

**Resume**
```bash
uv run inspect eval-retry <partial-log.eval> --max-connections 2 --retry-on-error 5 --log-dir results/logs/final_v1.0/nemotron-3-super/neutral
uv run inspect eval-retry <partial-log.eval> --max-connections 2 --retry-on-error 5 --log-dir results/logs/final_v1.0/nemotron-3-super/ethical
```

## 4. Inkling Small

**Smoke test**
```bash
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning --model openrouter/thinkingmachines/inkling-small:free --limit 2 --epochs 1 --max-connections 2 --retry-on-error 5 --log-dir results/logs/smoke_test/inkling-small/neutral
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning_welfare --model openrouter/thinkingmachines/inkling-small:free --limit 2 --epochs 1 --max-connections 2 --retry-on-error 5 --log-dir results/logs/smoke_test/inkling-small/ethical
```

**Full run**
```bash
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning --model openrouter/thinkingmachines/inkling-small:free --max-connections 2 --retry-on-error 5 --log-dir results/logs/final_v1.0/inkling-small/neutral
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning_welfare --model openrouter/thinkingmachines/inkling-small:free --max-connections 2 --retry-on-error 5 --log-dir results/logs/final_v1.0/inkling-small/ethical
```

**Resume**
```bash
uv run inspect eval-retry <partial-log.eval> --max-connections 2 --retry-on-error 5 --log-dir results/logs/final_v1.0/inkling-small/neutral
uv run inspect eval-retry <partial-log.eval> --max-connections 2 --retry-on-error 5 --log-dir results/logs/final_v1.0/inkling-small/ethical
```

## 5. Xing4.0 29B

**Smoke test**
```bash
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning --model openrouter/xingchen-agi/xing4.0-29b-a4b:free --limit 2 --epochs 1 --max-connections 2 --retry-on-error 5 --log-dir results/logs/smoke_test/xing4/neutral
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning_welfare --model openrouter/xingchen-agi/xing4.0-29b-a4b:free --limit 2 --epochs 1 --max-connections 2 --retry-on-error 5 --log-dir results/logs/smoke_test/xing4/ethical
```

**Full run**
```bash
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning --model openrouter/xingchen-agi/xing4.0-29b-a4b:free --max-connections 2 --retry-on-error 5 --log-dir results/logs/final_v1.0/xing4/neutral
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning_welfare --model openrouter/xingchen-agi/xing4.0-29b-a4b:free --max-connections 2 --retry-on-error 5 --log-dir results/logs/final_v1.0/xing4/ethical
```

**Resume**
```bash
uv run inspect eval-retry <partial-log.eval> --max-connections 2 --retry-on-error 5 --log-dir results/logs/final_v1.0/xing4/neutral
uv run inspect eval-retry <partial-log.eval> --max-connections 2 --retry-on-error 5 --log-dir results/logs/final_v1.0/xing4/ethical
```

## View results

```bash
uv run inspect view --log-dir results/logs/final_v1.0
```
