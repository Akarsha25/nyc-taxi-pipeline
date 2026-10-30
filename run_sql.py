"""Run SQL against taxi.duckdb.

  .venv/bin/python run_sql.py sql/reports.sql   # run every query in a file
  .venv/bin/python run_sql.py                               # interactive prompt (end queries with ;)
"""
import sys

import duckdb

con = duckdb.connect("taxi.duckdb")


def run(query: str) -> None:
    query = query.strip()
    if not query:
        return
    try:
        print(con.sql(query))
    except Exception as e:
        print(f"ERROR: {e}")


if len(sys.argv) > 1:
    text = open(sys.argv[1]).read()
    # Drop comment lines, then split on ; so each query prints its own result.
    code = "\n".join(line for line in text.splitlines() if not line.strip().startswith("--"))
    for q in code.split(";"):
        if q.strip():
            print(f"\n>>> {q.strip()}\n")
            run(q)
else:
    print("Tables: trips, drivers. End each query with ; — type 'exit' to quit.")
    buf = []
    while True:
        try:
            line = input("sql> " if not buf else "...> ")
        except EOFError:
            break
        if line.strip().lower() in ("exit", "quit"):
            break
        buf.append(line)
        if line.rstrip().endswith(";"):
            run("\n".join(buf))
            buf = []
