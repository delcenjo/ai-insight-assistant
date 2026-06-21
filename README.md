# AI Insight Assistant

![CI](https://github.com/delcenjo/ai-insight-assistant/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)

This is a small internal assistant for a made-up company (Helios). You ask it a
question in plain English and it figures out where the answer should come from:
the company handbook, or the employee database. Some questions are about written
policy, some are about numbers, and you should not have to know which is which
before you ask.

For example, ask *"how many vacation days do we get?"* and it pulls the relevant
passage out of the handbook. Ask *"What is the average salary in Engineering?"*
and it writes and runs a SQL query against the database instead. Same chat box,
two very different sources behind it.

## What's going on under the hood

There are two things the assistant can reach for:

- `search_docs` does retrieval (RAG) over the handbook: documents are chunked,
  embedded, and looked up by cosine similarity.
- `query_database` runs read-only SQL against a small company database, with a
  guard that rejects anything that tries to write.

An LLM sits in the middle as a tool-using agent. On each question it decides
whether to call one of those tools (or both), reads the results back, and then
writes the final answer. The agent loop just keeps going until the model stops
asking for tools.

```
                     ┌──────────────┐
   Streamlit UI ───▶ │ FastAPI /chat│ ───▶ LLM (tool use)
                     └──────────────┘            │
                          ▲             ┌─────────┴──────────┐
                          │             ▼                    ▼
                          │      search_docs            query_database
                          │      (RAG retrieval)        (read-only SQL)
                          │             │                    │
                          └──────── answer ◀── documents + employee data
```

## The HTTP API

The backend is FastAPI and exposes three endpoints:

| Method | Path       | What it does                                         |
| ------ | ---------- | ---------------------------------------------------- |
| GET    | `/health`  | liveness check                                       |
| POST   | `/search`  | document retrieval only (works without an API key)   |
| POST   | `/chat`    | full agent answer (needs an LLM API key)             |

`/search` is the cheap one: it never calls the model, so you can poke at the
retrieval layer on its own. Asking it *"how many vacation days do we get?"*
gives back the matching handbook chunk and a score:

```json
{ "source": "handbook.md", "text": "... 25 paid vacation days per year ...", "score": 0.61 }
```

The SQL side answers structured questions straight from the data. A grouped
query like this:

```
SELECT department, COUNT(*) AS headcount, ROUND(AVG(salary)) AS avg_salary
FROM employees GROUP BY department ORDER BY avg_salary DESC

Engineering  10  54400
Marketing     3  50333
HR            3  49000
Sales         5  48000
Support       4  38250
```

`/chat` is where the two come together. Given an LLM API key, *"What is the
remote-work policy?"* gets routed to `search_docs` and *"What is the average
salary in Engineering?"* to `query_database`, and the model writes the reply.
Without a key, `/chat` returns 503 and only `/search` stays usable.

## Layout

```
src/assistant/
  config.py     paths, model names, parameters
  retrieval.py  chunking, embeddings and cosine search (RAG)
  database.py   company database and read-only query guard
  tools.py      search_docs and query_database tools
  agent.py      LLM tool-use loop
  ingest.py     build the index and seed the database
  api.py        FastAPI backend
frontend/app.py Streamlit chat UI
tests/          retrieval, database and API tests
Dockerfile, docker-compose.yml   backend + frontend containers
```

## Running it locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,frontend]"

python -m assistant.ingest                 # build index + seed database
uvicorn assistant.api:app --reload         # backend at http://localhost:8000
streamlit run frontend/app.py              # UI at http://localhost:8501
pytest
```

The ingest step is what builds the document index and seeds the database, so run
it once before you start the backend. For `/chat` to work you'll need an LLM API
key set in your environment; everything else runs without one.

## Running it with Docker

If you'd rather not set up the environment by hand, Docker Compose brings up the
backend and frontend together:

```bash
docker compose up --build      # backend on :8000, frontend on :8501
```

## Where it fits

This one ties together a few things from the rest of the portfolio: the dense
retrieval from the RAG document assistant, the tool-use-over-SQL agent, and the
FastAPI plus Docker plus CI setup from the churn prediction API. It's less a new
idea than a place where those pieces have to cooperate on the same question.
