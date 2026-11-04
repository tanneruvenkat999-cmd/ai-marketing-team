# Autonomous AI Marketing Team — Venkat Tanniru

A runnable seven-agent drafting prototype for local businesses. Each agent has its own editable prompt in `agents/`. Python orchestrates their handoffs and records a CSV task ledger. No third-party Python packages are required. Requires Python 3.10 or newer.

## Start without an API key

Clone or download this repository, open a terminal in its root folder, then run:

```sh
python run.py run --demo --out my_demo_campaign
```

This validates the workflow with clearly labeled placeholders. It does not create real AI marketing content. A completed example is included in `demo_campaign/`.

## Generate real drafts

1. Copy `brief.example.json` to `brief.json` and replace the fictional business details.
2. Add verified product facts, brand guidelines, source excerpts and URLs under `sources`, and any real analytics under `metrics`. A URL alone is not fetched. Remove personal customer information that is not needed.
3. Set your API key privately in your terminal. Never put it in the brief, source code or GitHub.

Windows PowerShell:
```powershell
$env:OPENAI_API_KEY="YOUR_API_KEY"
python run.py run --brief brief.json --out first_campaign --model YOUR_MODEL_ID
```

macOS/Linux:
```sh
export OPENAI_API_KEY="YOUR_API_KEY"
python run.py run --brief brief.json --out first_campaign --model YOUR_MODEL_ID
```

Replace YOUR_MODEL_ID with a Responses-compatible model available to your API account. Live mode makes seven sequential paid API calls and sends the brief and upstream drafts to OpenAI. ChatGPT access does not itself configure an API key for this project.

## Your seven agents

| Agent | Deliverable |
|---|---|
| Project Manager | Task plan, deadlines, blockers and executive brief draft |
| Market & Audience Researcher | Evidence-based audience hypotheses and competitor comparison |
| Campaign Strategist | Campaign brief and four-week calendar |
| Marketing Copywriter | Captions, ads, email draft and short video script |
| Visual Content Designer | Design specifications, image prompts and storyboard |
| Quality & Publishing Coordinator | Review checklist and proposed publishing calendar |
| Performance Analyst | Metrics analysis, or measurement plan when data is absent |

The order is manager → research → strategy → copy → design → quality → analysis. Copy and design are provisional drafts until strategy approval. No approval is inferred from an agent's text. The orchestrator stores outputs and records completed draft steps in tasks.csv, which you can import into Google Sheets. Unknown deadlines stay unknown.

## Outputs and review

Each run creates seven Markdown deliverables, a snapshot of the brief, tasks.csv and review.json. Use a new output folder for every run; existing folders are never overwritten. If an API call fails, earlier completed outputs remain available, but no complete review package is issued. Correct the problem and start a new run.

Read the strategy, all content and the quality checklist. Fix source facts or prompts and re-run if changes are needed. A local review can be recorded with:

```sh
python run.py approve first_campaign --reviewer "Venkat Tanniru" --scope content
```

This records a review of the exact package hash. Demo packages and changed packages are rejected. This is a local record, not authenticated client approval or authorization to send or spend. Review records do not execute anything. Publishing, promotional email, executive-brief email delivery and ad spend remain manual and require explicit authorization for the exact destination, content, schedule and budget.

## Integration status and limits

- OpenAI drafting: implemented; requires your key and model. Live calls have not been tested with a real key in this delivery.
- Google Sheets: CSV export only; no automatic sync.
- Gmail: drafts only; no sending or daily scheduling.
- Social platforms: calendar proposals only; no scheduling or publishing API.
- Web research: supplied evidence only; no live crawler/search connector.
- Graphics: design briefs and image prompts only; no bitmap generation.
- Analytics: supplied data only; no connected accounts.
- Approvals: local review record only; not a multi-user permissions system.

These boundaries prevent the prototype from claiming actions it cannot perform. To make it an always-running agency, connect the chosen services, add authenticated approval handling, scheduling, retries and monitoring. Never give model-generated text direct authority to publish or spend.

## Verification

```sh
python -m unittest -v
```

Tests cover the seven-step workflow, approval rejection for demo content, edited-package rejection and mocked live response handoff. API implementation reference: https://developers.openai.com/api/reference/resources/responses/methods/create
