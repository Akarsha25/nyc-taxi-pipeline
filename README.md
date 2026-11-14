# NYC Taxi Data Pipeline

An end-to-end data engineering project on public NYC Taxi & Limousine Commission (TLC) trip data:
raw files cleaned and modelled into a star schema with dbt (with data tests), orchestrated by Airflow,
business reports in SQL, and an AI agent that answers questions about the warehouse.

> Status: Phases 1–4 done (January 2024, 2.75M trips), orchestrated daily with Airflow. Next: Spark.

## Architecture

```
TLC trip data (raw Parquet, Jan 2024, 2.96M rows)
        │
        ▼
dbt  ── staging/stg_trips.sql : 5 cleaning rules + renamed columns (2.75M rows kept, 7.1% rejected)
        │
        ▼
Star schema (DuckDB, schema "dbt"):  fact_trips + dim_zone, dim_date, dim_payment, dim_vendor, dim_rate_code
        │   11 dbt tests (unique, not_null, relationships, custom cleaning-rule test)
        │
        ├──► sql/reports.sql      business reports R1–R5
        └──► src/agent_full.py    AI agent: question in English → SQL → answer

Airflow runs  dbt run >> dbt test  every day at 6 AM.
```

The first version of the pipeline did the cleaning in Python (`src/ingest.py`, `src/load.py`) and the
modelling in `src/model.py`. Those scripts are kept for reference; dbt now does all of it from the raw file.

## Roadmap

| Phase | Adds | Status |
|---|---|---|
| 1 | Python ingestion, data-quality checks, DuckDB | done |
| 2 | Star schema (1 fact + 5 dimension tables) and business reports | done |
| 2b | Agentic AI v1: an agent that answers questions about the warehouse with a read-only SQL tool | done |
| 3 | dbt models (staging + marts) and data tests; cleaning moved from Python into dbt | done |
| 4 | Airflow DAG: dbt run → dbt test, daily at 6 AM | done |
| 5 | Spark for multi-month / large-scale processing | next |
| 6 | Docker packaging | planned |
| 7 | Agentic AI layer: more tools (describe_tables, read_pipeline_log), pipeline investigation | planned |

## dbt (Phase 3)

```
taxi_dbt/models/
  staging/  stg_trips.sql                      ← reads the raw file, applies the 5 cleaning rules
  marts/    fact_trips.sql + 5 dim_*.sql       ← the star schema, built with ref()
  schema.yaml                                  ← 10 generic tests
taxi_dbt/tests/
  asserts_trips.sql                            ← custom test: no row breaks a cleaning rule
```

Tests: `unique` and `not_null` on keys, `relationships` tests that every trip's pickup zone and
payment type exist in their dimensions (referential integrity), and a custom test that no trip breaks
a cleaning rule. All 7 models build and all 11 tests pass.

## Airflow (Phase 4)

`dags/taxi_pipeline.py` runs the whole pipeline every day at 6 AM, in order:

```
dbt_run  >>  dbt_test
```

Each task runs one command with a `BashOperator`. If a step fails (for example a dbt test),
the following steps do not run, so bad data never reaches the reports or the agent.

```bash
python3 -m venv .venv-airflow
.venv-airflow/bin/pip install "apache-airflow==2.10.5" \
  --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-3.9.txt"
export PATH=$PWD/.venv-airflow/bin:$PATH AIRFLOW_HOME=$PWD/airflow_home \
       AIRFLOW__CORE__DAGS_FOLDER=$PWD/dags AIRFLOW__CORE__LOAD_EXAMPLES=False NO_PROXY="*"
airflow standalone          # web UI at http://localhost:8080
```

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

cd taxi_dbt                               # clean the raw file and build the star schema
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
| dbt models / tests | 7 / 11, all passing |
| Airflow DAG run | all tasks succeeded |
| agent evaluation | 3/3 correct |

**Key findings**
- JFK Airport is the top pickup zone by revenue: **$11.17M**, nearly double LaGuardia ($5.79M).
- Weekdays average ~93K trips a day vs ~78K on weekends; weekend fares are about 4% lower.
- Card trips tip **22.6%** of the fare. Cash trips show 0% because cash tips are never recorded
  by the meter, so 0 means "not recorded", not "no tip".

## Data source

[NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
