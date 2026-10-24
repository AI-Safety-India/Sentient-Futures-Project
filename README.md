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

1. Pilot run: category C1 (`killing_slaughter_method`), 1 epoch, neutral + ethical.
2. Full run: all categories, 3 epochs, neutral + ethical.
3. If a run stops, resume it into the same folder, then delete the old partial log:

```bash
uv run inspect eval-retry <partial-log.eval> --max-connections 2 --retry-on-error 5 --log-dir <same-folder-as-the-stopped-run>
```

## 1. Nemotron 3 Ultra

**Pilot run**
```bash
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning --model openrouter/nvidia/nemotron-3-ultra-550b-a55b:free -T categories=killing_slaughter_method --epochs 1 --max-connections 2 --retry-on-error 5 --log-dir results/logs/pilot/nemotron-3-ultra/neutral
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning_welfare --model openrouter/nvidia/nemotron-3-ultra-550b-a55b:free -T categories=killing_slaughter_method --epochs 1 --max-connections 2 --retry-on-error 5 --log-dir results/logs/pilot/nemotron-3-ultra/ethical
```

**Full run**
```bash
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning --model openrouter/nvidia/nemotron-3-ultra-550b-a55b:free --max-connections 2 --retry-on-error 5 --log-dir results/logs/final_v1.0/nemotron-3-ultra/neutral
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning_welfare --model openrouter/nvidia/nemotron-3-ultra-550b-a55b:free --max-connections 2 --retry-on-error 5 --log-dir results/logs/final_v1.0/nemotron-3-ultra/ethical
```

## 2. Nemotron 3 Super

**Pilot run**
```bash
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning --model openrouter/nvidia/nemotron-3-super-120b-a12b:free -T categories=killing_slaughter_method --epochs 1 --max-connections 2 --retry-on-error 5 --log-dir results/logs/pilot/nemotron-3-super/neutral
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning_welfare --model openrouter/nvidia/nemotron-3-super-120b-a12b:free -T categories=killing_slaughter_method --epochs 1 --max-connections 2 --retry-on-error 5 --log-dir results/logs/pilot/nemotron-3-super/ethical
```

**Full run**
```bash
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning --model openrouter/nvidia/nemotron-3-super-120b-a12b:free --max-connections 2 --retry-on-error 5 --log-dir results/logs/final_v1.0/nemotron-3-super/neutral
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning_welfare --model openrouter/nvidia/nemotron-3-super-120b-a12b:free --max-connections 2 --retry-on-error 5 --log-dir results/logs/final_v1.0/nemotron-3-super/ethical
```

## 3. Inkling Small

**Pilot run**
```bash
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning --model openrouter/thinkingmachines/inkling-small:free -T categories=killing_slaughter_method --epochs 1 --max-connections 2 --retry-on-error 5 --log-dir results/logs/pilot/inkling-small/neutral
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning_welfare --model openrouter/thinkingmachines/inkling-small:free -T categories=killing_slaughter_method --epochs 1 --max-connections 2 --retry-on-error 5 --log-dir results/logs/pilot/inkling-small/ethical
```

**Full run**
```bash
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning --model openrouter/thinkingmachines/inkling-small:free --max-connections 2 --retry-on-error 5 --log-dir results/logs/final_v1.0/inkling-small/neutral
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning_welfare --model openrouter/thinkingmachines/inkling-small:free --max-connections 2 --retry-on-error 5 --log-dir results/logs/final_v1.0/inkling-small/ethical
```

## 4. Xing4.0 29B

**Pilot run**
```bash
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning --model openrouter/xingchen-agi/xing4.0-29b-a4b:free -T categories=killing_slaughter_method --epochs 1 --max-connections 2 --retry-on-error 5 --log-dir results/logs/pilot/xing4/neutral
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning_welfare --model openrouter/xingchen-agi/xing4.0-29b-a4b:free -T categories=killing_slaughter_method --epochs 1 --max-connections 2 --retry-on-error 5 --log-dir results/logs/pilot/xing4/ethical
```

**Full run**
```bash
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning --model openrouter/xingchen-agi/xing4.0-29b-a4b:free --max-connections 2 --retry-on-error 5 --log-dir results/logs/final_v1.0/xing4/neutral
uv run inspect eval domains/menu_planning/eval/task.py@menu_planning_welfare --model openrouter/xingchen-agi/xing4.0-29b-a4b:free --max-connections 2 --retry-on-error 5 --log-dir results/logs/final_v1.0/xing4/ethical
```

## View results

```bash
uv run inspect view --log-dir results/logs
```
