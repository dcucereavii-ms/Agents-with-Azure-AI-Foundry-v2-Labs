# Lab 4 — Evaluate, Iterate, Promote

Build a production-quality gate around an agent: run it live against a fixed
test suite, fail the gate on weak instructions, fix the instructions, re-run,
and promote the passing version.

> **Note on the directory name:** `lab4-eval-teams` is kept for backward-compat
> with earlier workshop links. The Teams deployment step has been removed —
> in Foundry v2 the realistic promotion artifact is agent metadata + a
> Playground URL, not a Teams app package.

## Goals

- Define a fixed evaluation dataset of (query, ground_truth, context) cases.
- Run the agent **live** for each case (no pre-canned responses).
- Score every response with LLM judges (groundedness, coherence, relevance)
  plus a deterministic citation evaluator.
- Watch a weak agent fail the quality gate, fix it, watch a strong agent pass.
- Promote the passing agent by stamping metadata and sharing the Playground URL.

## Prerequisites

- Azure AI Foundry project (same one used in Labs 1–3).
- A model deployment (e.g. `gpt-4o`) reachable via the project.
- An Azure OpenAI endpoint for the **judge** model (`AZURE_OPENAI_ENDPOINT` in
  `.env`). Auth is Entra ID via `DefaultAzureCredential` -- no key required.
- `pip install -r requirements.txt` from the lab folder.

## File map

```
lab4-eval-teams/
├── starter/
│   ├── agent_under_test.py      # weak + strong agent builders
│   ├── evaluate.py              # TODOs to fill in
│   ├── promote.py               # TODOs to fill in
│   └── datasets/eval_cases.jsonl
└── solution/
    ├── agent_under_test.py
    ├── evaluate.py
    ├── promote.py
    └── datasets/eval_cases.jsonl
```

## Walkthrough

### Step 1 — Inspect the dataset

`datasets/eval_cases.jsonl` contains only `query`, `ground_truth`, and `context`.
There is no `response` field — the agent generates that live during evaluation.
This is the difference between a *real* eval and a fixture replay.

### Step 2 — Wire up the live target

In `evaluate.py`, complete `make_agent_target()`. For each row the function
should:

1. Create a thread.
2. Post a user message containing the `context` and the `query`.
3. Run the agent to completion.
4. Return `{"response": <assistant text>}`.

The evaluation SDK calls this once per row and feeds the returned `response`
into each evaluator.

### Step 3 — Run v1 (weak)

> ⏱ **Workshop timing:** each variant run is a live evaluation against the agent and takes **~3–5 minutes**. `--variant both` therefore takes **5–11 minutes**. If you're tight on time, run **`--variant strong` first** (it's the one that passes) to see the gate green, then run `--variant weak` only if time permits.

```bash
python evaluate.py --variant weak
```

`agent_under_test.create_weak_agent()` uses minimal instructions
(*"Answer briefly."*). Expect the groundedness/citation gates to fail —
the agent hallucinates or paraphrases without grounding in the provided context.

Inspect the raw `results["metrics"]` dict that prints before the gate table.
That's where you find out whether the SDK on your machine emits keys like
`groundedness` or `groundedness.groundedness`. Make your gate tolerant of both.

### Step 4 — Run v2 (strong)

```bash
python evaluate.py --variant strong
```

`create_strong_agent()` requires the agent to ground every answer in the
provided context and cite specific concepts/classes. Expect the gate to pass.

You can also run both variants in one pass and compare:

```bash
python evaluate.py --variant both
```

### Step 5 — Promote

When the strong variant passes:

```bash
python evaluate.py --variant strong --promote
```

or run promotion directly:

```bash
python promote.py --agent-id <id-from-evaluate-output>
```

`promote.py` stamps the agent with metadata
(`promoted=true`, `promoted_version`, `promoted_at`, `eval_status`)
and prints the Foundry Playground URL.

### Step 6 — Verify in Foundry

Open the Playground URL. Confirm the metadata is visible on the agent's
detail panel and the agent responds with grounded, cited answers.

## What changed from v1 of this lab

| Old | New |
|---|---|
| `response` baked into the dataset → evaluators scored a string the agent never produced. | Live agent target — every response is real. |
| One agent, one run, pass/fail with no iteration story. | Weak → fix → strong iteration loop is the main flow. |
| `teams_deploy.py` produced an app manifest that needed sideloading. | `promote.py` stamps metadata + prints the Playground URL. |
| No deterministic signal — the gate died when the judge LLM was rate-limited. | `CitationPresentEvaluator` gives the gate a regex-based baseline. |

## Troubleshooting

- **`KeyError: 'AZURE_OPENAI_ENDPOINT'`** — the judge config is separate from
  the project endpoint. Add both to `.env`.
- **Gate prints `MISSING` for every metric** — your SDK version is emitting
  prefixed keys (`groundedness.groundedness`). Implement the tolerant lookup
  shown in TODO 5.
- **Run never completes** — check that the agent's tool config is valid.
- **Agents accumulate in the project** — `evaluate.py` deletes the agents it
  created in a `finally` block; if you Ctrl-C during a run, run
  `client.agents.list_agents()` and clean up manually.
