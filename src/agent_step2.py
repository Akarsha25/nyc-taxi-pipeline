"""AGENT STEP 2: tell Claude about a tool, and see it ASK to use it.
Nothing runs on the database yet - we only print what Claude asks for.
Run (in the Terminal window that has your key):  .venv/bin/python src/agent_step2.py
"""
import anthropic

client = anthropic.Anthropic()

SCHEMA = """Tables in the NYC taxi warehouse (DuckDB):
fact_trips (trip_id, pickup_zone_id, dropoff_zone_id, payment_type_id, vendor_id, rate_code_id,
            pickup_date, trip_distance, trip_minutes, fare_amount, tip_amount, total_amount)
dim_zone (zone_id, borough, zone_name, service_zone)
dim_date (date_key, day_name, is_weekend, week_start, month_name, is_holiday, holiday_name)
dim_payment (payment_type_id, payment_name)
Joins: fact_trips.pickup_zone_id = dim_zone.zone_id, fact_trips.pickup_date = dim_date.date_key,
       fact_trips.payment_type_id = dim_payment.payment_type_id"""

tools = [{                                            # line A: describe the tool to Claude
    "name": "run_sql",
    "description": "Run one read-only SELECT query on the NYC taxi warehouse and return the rows.",
    "input_schema": {
        "type": "object",
        "properties": {"query": {"type": "string", "description": "One DuckDB SELECT statement"}},
        "required": ["query"],
    },
}]

response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=2000,
    system="You are a data analyst for NYC taxi data. Answer by querying the warehouse.\n" + SCHEMA,  # line B
    tools=tools,                                      # line C: hand Claude the tool list
    messages=[{"role": "user", "content": "Which pickup zone made the most revenue?"}],
)

print("stop_reason:", response.stop_reason)          # line D: "tool_use" = Claude wants to use a tool
for block in response.content:
    if block.type == "tool_use":                      # line E: Claude's request
        print("Claude wants to run:", block.name)
        print("with this SQL:\n", block.input["query"])
