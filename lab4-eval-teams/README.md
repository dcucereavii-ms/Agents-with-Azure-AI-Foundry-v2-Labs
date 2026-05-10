# Lab 4 — Ship It: Eval Gate + Live Deployment to Teams

**Duration:** 35 minutes  
**Skill level:** Intermediate / Advanced

---

## 🎯 What You'll Build

An **evaluation pipeline** that automatically scores your agent's responses against quality thresholds, and a **Teams-ready agent** configured for deployment in Microsoft Teams.

```
┌─────────────────────────────────────────────────────────────┐
│  evaluate.py                                                │
│                                                             │
│  eval_cases.jsonl → [GroundednessEvaluator]                │
│                     [CoherenceEvaluator  ]  → Scores       │
│                     [RelevanceEvaluator  ]      │           │
│                                                 ▼           │
│                              eval_gate() → PASS / FAIL      │
│                                    │                        │
│                              (if PASS)                      │
│                                    ▼                        │
│  teams_deploy.py → TeamsAssistant-Production agent          │
│                 → Azure AI Foundry → Channels → Teams       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Lab Setup

```bash
cd lab4-eval-teams
pip install -r requirements.txt
```

Confirm your `.env` has:
- `AIPROJECT_ENDPOINT`
- `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_KEY` (for evaluators — instructor provides)
- `MODEL_DEPLOYMENT`

---

## Step 1 — Review the Evaluation Dataset

Open `starter/datasets/eval_cases.jsonl`. Each line is a JSON object with:

| Field | Description |
|---|---|
| `query` | The question asked of the agent |
| `response` | The agent's response (what we're evaluating) |
| `ground_truth` | The correct/expected answer |
| `context` | Background context used by the agent |

Look through the 8 test cases. Notice they cover different scenarios:
- Factual questions about Azure AI
- Conceptual explanations
- Step-by-step guides
- Comparison questions

**Question to consider:** Which test cases do you expect to score lowest on Groundedness? Why?

---

## Step 2 — Implement the Evaluation Runner

Open `starter/evaluate.py`. Implement `run_evaluation()`:

```python
from azure.ai.evaluation import (
    RelevanceEvaluator,
    CoherenceEvaluator,
    GroundednessEvaluator,
    evaluate,
)

def run_evaluation(project_client):
    model_config = {
        "azure_endpoint": os.environ["AZURE_OPENAI_ENDPOINT"],
        "api_key": os.environ["AZURE_OPENAI_KEY"],
        "azure_deployment": os.environ.get("MODEL_DEPLOYMENT", "gpt-4o"),
        "api_version": "2024-08-01-preview",
    }
    
    evaluators = {
        "groundedness": GroundednessEvaluator(model_config=model_config),
        "coherence": CoherenceEvaluator(model_config=model_config),
        "relevance": RelevanceEvaluator(model_config=model_config),
    }
    
    results = evaluate(
        data=str(DATASET_PATH),
        evaluators=evaluators,
        output_path="eval_results.json",
    )
    return results
```

> 💡 **How it works:** The `evaluate()` function loads your JSONL dataset, calls each evaluator on every row, aggregates scores, and saves detailed results to `eval_results.json`. Evaluators use a judge LLM (your gpt-4o deployment) to score responses.

---

## Step 3 — Run Evaluations and Review Scores

```bash
cd starter
python evaluate.py
```

This takes **1-2 minutes** while the judge LLM processes each test case.

You'll see output like:
```
🔍 Running Evaluation Suite
Loaded 8 evaluation cases from eval_cases.jsonl
Running evaluators... (this takes 1-2 minutes)

┌─────────────────┬───────┬───────────┬────────┐
│ Metric          │ Score │ Threshold │ Status │
├─────────────────┼───────┼───────────┼────────┤
│ groundedness    │  4.1  │    3.5    │  PASS  │
│ coherence       │  4.3  │    3.5    │  PASS  │
│ relevance       │  3.8  │    3.5    │  PASS  │
└─────────────────┴───────┴───────────┴────────┘
✅ QUALITY GATE PASSED
```

Open `eval_results.json` to see per-row scores and see which test cases scored lowest.

---

## Step 4 — Implement the Eval Gate

Still in `starter/evaluate.py`, implement `eval_gate()`:

```python
def eval_gate(results: dict) -> bool:
    metrics = results.get("metrics", {})
    
    table = Table(title="Evaluation Results")
    table.add_column("Metric")
    table.add_column("Score", justify="right")
    table.add_column("Threshold", justify="right")
    table.add_column("Status")
    
    all_pass = True
    for name, threshold in EVAL_THRESHOLDS.items():
        # Metric keys use the format "evaluator_name.metric_name"
        key = f"{name}.{name}"
        score = metrics.get(key, 0.0)
        passed = score >= threshold
        all_pass = all_pass and passed
        
        status = "[green]PASS[/green]" if passed else "[red]FAIL[/red]"
        table.add_row(name, f"{score:.2f}", f"{threshold:.1f}", status)
    
    console.print(table)
    return all_pass
```

> 💡 **Threshold tuning:** The default thresholds (3.5/5) are deliberately achievable with well-crafted responses. In production, you'd raise these after your baseline is established.

---

## Step 5 — Configure Teams Deployment

Open `starter/teams_deploy.py` and review `create_teams_ready_agent()`. This is pre-built.

Run it:

```bash
python teams_deploy.py
```

The output will guide you through the portal steps to add the Teams channel.

**Portal steps (follow along with the instructor):**
1. Go to [ai.azure.com](https://ai.azure.com) → your project → **Agents**
2. Find `TeamsAssistant-Production`
3. Click **Channels** → **Microsoft Teams**
4. Follow the wizard to generate a Teams app manifest
5. In Microsoft Teams: click **Apps** → **Upload a custom app** → upload the manifest zip
6. Test by typing `@TeamsAssistant-Production Hello!` in any Teams channel

---

## Step 6 — (Optional) Deploy If Gate Passes

Modify `main()` in `evaluate.py` to call `teams_deploy.py` only when the gate passes:

```python
if passed:
    console.print("Running Teams deployment...")
    import subprocess
    subprocess.run([sys.executable, "teams_deploy.py"], check=True)
```

---

## ✅ Success Criteria

- [ ] `python evaluate.py` runs without errors
- [ ] All 3 evaluators return scores (not 0 or error)
- [ ] The results table displays with PASS/FAIL per metric
- [ ] `eval_results.json` is created with per-row details
- [ ] `python teams_deploy.py` creates the agent and shows deployment steps
- [ ] (Optional) Teams app manifest is downloaded and uploaded to Teams

---

## 🏆 Bonus Challenges

### Bonus 1 — Add a Custom Evaluator
Create a custom evaluator that checks if responses mention Azure-specific services:
```python
def azure_specificity_evaluator(query, response, **kwargs):
    azure_terms = ["azure", "microsoft", "foundry", "openai"]
    score = sum(1 for term in azure_terms if term in response.lower())
    return {"azure_specificity": min(score / 2, 5.0)}
```
Add it to the `evaluators` dict in `run_evaluation()`.

### Bonus 2 — Adjust Thresholds
Increase `EVAL_THRESHOLDS` values to `4.0` and re-run. How many cases fail? What does this tell you about dataset quality?

### Bonus 3 — Baseline vs Optimized
Modify 2-3 responses in `eval_cases.jsonl` to be lower quality (vague, off-topic). Re-run and watch the gate fail. Then restore and observe the gate pass again.

---

## 💡 Key Concepts

| Concept | What It Is |
|---|---|
| **Groundedness** | Does the response accurately reflect the provided context/facts? |
| **Coherence** | Is the response logically structured and easy to follow? |
| **Relevance** | Does the response address the actual question asked? |
| **Judge LLM** | A second LLM instance that scores responses (GPT-4o used here) |
| **Eval gate** | Automated pass/fail check on metric averages before deployment |
| **Teams channel** | Azure AI Foundry feature that exposes your agent as a Teams bot |
| **App manifest** | JSON package that registers your Teams bot in the Teams ecosystem |
