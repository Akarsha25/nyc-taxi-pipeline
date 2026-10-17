# NYC Taxi Data Pipeline

An end-to-end data engineering project on public NYC Taxi & Limousine Commission (TLC) trip data.

> Status: Phase 1 in progress (batch ingestion + SQL analytics)

## Goal

Ingest raw monthly taxi trip files, validate and clean them, load them into an analytical
database, and model them for analysis. The project grows in phases toward a production-style
stack (orchestration, transformations as code, distributed processing).

## Architecture (Phase 1)

```
TLC trip data (Parquet, monthly)
        │  download
        ▼
data/raw/            ← untouched source files
        │  src/ingest.py : validate, clean, count rejects
        ▼
data/processed/      ← clean Parquet
        │  load
        ▼
DuckDB (taxi.duckdb) ← SQL analysis in sql/
```

## Roadmap

| Phase | Adds | Status |
|---|---|---|
| 1 | Python ingestion, data-quality checks, DuckDB, SQL analysis | in progress |
| 2 | Star schema (fact + dimension tables) | planned |
| 2b | Agentic AI v1: an agent that answers questions about the warehouse using a read-only SQL tool (expanded in Phase 7) | planned |
| 3 | dbt models and tests | planned |
| 4 | Airflow scheduling, idempotent backfills | planned |
| 5 | Spark for multi-month / large-scale processing | planned |
| 6 | Docker packaging | planned |
| 7 | Agentic AI layer: an LLM agent with read-only tools (run_sql, describe_tables, read_pipeline_log) that answers business questions, investigates pipeline issues, and drafts new transformations for review | planned |

## How to run

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python src/ingest.py
```

## Data source

[NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)

## Results

_To be filled in: row counts, rejected rows, runtime, key findings._
