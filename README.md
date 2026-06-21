# AI Insight Assistant

![CI](https://github.com/delcenjo/ai-insight-assistant/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)

A capstone project that brings the rest of the portfolio together: an internal
assistant that answers questions about a company by combining **retrieval over
documents (RAG)** and a **tool-using agent that queries a database**, served
through a **FastAPI** backend with a **Streamlit** chat frontend and packaged
with **Docker Compose**.

The model decides, per question, whether to search the handbook or query the
employee database - the same agentic tool-use pattern, applied to two very
different knowledge sources.

## Architecture

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

## Endpoints

| Method | Path       | Description                                          |
| ------ | ---------- | ---------------------------------------------------- |
| GET    | `/health`  | liveness check                                       |
| POST   | `/search`  | document retrieval only (works without an API key)   |
| POST   | `/chat`    | full agent answer (requires an LLM API key)     |

### Real examples

`POST /search` with *"how many vacation days do we get?"* returns the relevant
handbook passage:

```json
{ "source": "handbook.md", "text": "... 25 paid vacation days per year ...", "score": 0.61 }
```

The SQL tool answers structured questions directly from the database:

```
SELECT department, COUNT(*) AS headcount, ROUND(AVG(salary)) AS avg_salary
FROM employees GROUP BY department ORDER BY avg_salary DESC

Engineering  10  54400
Marketing     3  50333
HR            3  49000
Sales         5  48000
Support       4  38250
```

With an API key, `/chat` routes *"What is the remote-work policy?"* to
`search_docs` and *"What is the average salary in Engineering?"* to
`query_database`, then writes the final answer.

## Project structure

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

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,frontend]"

python -m assistant.ingest                 # build index + seed database
uvicorn assistant.api:app --reload         # backend at http://localhost:8000
streamlit run frontend/app.py              # UI at http://localhost:8501
pytest
```

## Run with Docker

```bash
docker compose up --build      # backend on :8000, frontend on :8501
```

## How it relates to the rest of the portfolio

This project reuses and combines the techniques built earlier: dense retrieval
(RAG document assistant), the tool-use agent over SQL (LLM SQL agent), and the
FastAPI + Docker + CI deployment setup (churn prediction API).

## Possible improvements

- Streaming responses and multi-turn memory passed to the agent.
- A re-ranking step and hybrid search for retrieval.
- Authentication and per-user access control on the database tool.
