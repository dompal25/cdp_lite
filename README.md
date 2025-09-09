# CDP Sandbox (with AI‑Predicted Segments)

Local, self-contained Customer Data Platform (CDP) that:
- Ingests Segment-style events (`track`, `identify`, `page`)
- Resolves identities deterministically
- Builds daily features (RFM, engagement)
- Creates segments via YAML **rules** and **ML propensity** scores
- Serves a REST API (FastAPI), CLI (Typer), and a simple UI (Streamlit)

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# seed data, build features, train a simple model
python -m src.cdp.cli seed --users 1000 --days 120
python -m src.cdp.cli features-build
python -m src.cdp.cli train-propensity

# run API & UI
uvicorn src.cdp.api.main:app --reload
streamlit run ui/app.py
```

### Preview a segment
```bash
curl 'http://127.0.0.1:8000/v1/segments/likely_to_buy_30d?limit=25'
```

## Project Structure
```
cdp-sandbox/
├─ src/cdp/
│  ├─ api/ (FastAPI)
│  ├─ ingest/ (schemas, writer)
│  ├─ identity/ (graph)
│  ├─ features/ (build → DuckDB SQL)
│  ├─ segments/ (rules + ml engines)
│  ├─ ml/ (training, metrics)
│  ├─ utils/ (storage, time)
│  └─ cli.py (Typer CLI)
├─ ui/app.py (Streamlit)
├─ data/ (duckdb, parquet, artifacts)
└─ tests/
```
