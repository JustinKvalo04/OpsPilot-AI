# OpsPilot AI — Starter

A learning project for an enterprise AI operations platform. This first version is a local API with an in-memory ticket store. Data is lost when the server restarts; no LLM or external integrations are included yet.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Visit http://127.0.0.1:8000/docs to create and list tickets.

## Test

```bash
pytest -q
```
