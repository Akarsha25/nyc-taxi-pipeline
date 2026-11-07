# NYC Taxi Data Pipeline

An end-to-end data engineering project on public NYC Taxi & Limousine Commission (TLC) trip data:
ingestion and validation in Python, a star schema in DuckDB, the same model rebuilt in dbt with
data tests, business reports in SQL, and an AI agent that answers questions about the warehouse.

> Status: Phases 1, 2, 2b and 3 done (January 2024, 2.75M trips). Next: Airflow.

## Architecture

```
TLC trip data (Parquet, Jan 2024, 2.96M rows)
        │  src/ingest.py : 5 validation rules, count rejects
        ▼
data/processed/      ← clean Parquet (2.75M rows, 7.1% rejected)
        │  src/load.py
        ▼
DuckDB (taxi.duckdb)
        │  src/model.py   or   taxi_dbt/ (dbt models + tests)
        ▼
Star schema:  fact_trips + dim_zone, dim_date, dim_payment, dim_vendor, dim_rate_code
        │
        ├──► sql/reports.sql      business reports R1–R5
        └──► src/agent_full.py    AI agent: question in English → SQL → answer
```

## Roadmap

| Phase | Adds | Status |
|---|---|---|
| 1 | Python ingestion, data-quality checks, DuckDB | done |
| 2 | Star schema (1 fact + 5 dimension tables) and business reports | done |
| 2b | Agentic AI v1: an agent that answers questions about the warehouse with a read-only SQL tool | done |
| 3 | dbt models (staging + marts) and data tests | done |
| 4 | Airflow scheduling, idempotent backfills | next |
| 5 | Spark for multi-month / large-scale processing | planned |
| 6 | Docker packaging | planned |
| 7 | Agentic AI layer: more tools (describe_tables, read_pipeline_log), pipeline investigation | planned |

## dbt (Phase 3)

```
taxi_dbt/models/
  staging/  stg_trips.sql                      ← renamed, cleaned trips
  marts/    fact_trips.sql + 5 dim_*.sql       ← the star schema, built with ref()
  schema.yaml                                  ← 6 data tests
```

Tests: `unique` and `not_null` on keys, and a `relationships` test that every trip's
pickup zone exists in `dim_zone` (referential integrity). All 7 models build and all 6 tests pass.

## AI agent (Phase 2b)

`src/agent_full.py`: Claude writes SQL for a question in plain English, the agent runs it
on the warehouse through a **read-only** `run_sql` tool (max 20 rows, errors sent back so the
model can fix its query, max 5 rounds), and the model turns the result into an answer.

**Evaluation** (`src/evaluate.py`): questions with known answers from the hand-written reports.
Score: **3/3** (top revenue zone, trips on 2024-01-01, weekend trips).

The API key is read from the `ANTHROPIC_API_KEY` environment variable and is never stored in the repo.

## How to run

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

.venv/bin/python src/ingest.py            # validate and clean
.venv/bin/python src/load.py              # load into DuckDB
.venv/bin/python src/model.py             # build the star schema (Python version)

cd taxi_dbt                               # or build it with dbt
../.venv/bin/dbt run --profiles-dir .
../.venv/bin/dbt test --profiles-dir .
cd ..

.venv/bin/python run_sql.py sql/reports.sql      # business reports

export ANTHROPIC_API_KEY=...              # your own key
.venv/bin/python src/agent_full.py        # ask questions in English
.venv/bin/python src/evaluate.py          # score the agent
```

## Results (January 2024)

| Metric | Value |
|---|---|
| raw trips | 2,964,624 |
| kept after validation | 2,754,870 |
| rejected | 209,754 (7.1%) |
| dbt models / tests | 7 / 6, all passing |
| agent evaluation | 3/3 correct |

**Key findings**
- JFK Airport is the top pickup zone by revenue: **$11.17M**, nearly double LaGuardia ($5.79M).
- Weekdays average ~93K trips a day vs ~78K on weekends; weekend fares are about 4% lower.
- Card trips tip **22.6%** of the fare. Cash trips show 0% because cash tips are never recorded
  by the meter, so 0 means "not recorded", not "no tip".

## Data source

[NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
