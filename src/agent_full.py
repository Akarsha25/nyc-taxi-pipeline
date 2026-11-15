import os
import anthropic
import duckdb

# --- read the API key from the .env file (never committed: .env is in .gitignore) ---
if os.path.exists(".env"):
    for line in open(".env"):
        if "=" in line:
            name, value = line.strip().split("=", 1)
            os.environ[name] = value          # the .env key wins over any old value in the terminal

# --- A. open the database (read-only) ---
con = duckdb.connect("taxi.duckdb", read_only=True)

# --- B. the hands: run SQL, return up to 20 rows ---
def run_sql(query):
    try:
        rows = con.sql(query).fetchall()
        return str(rows[:20])
    except Exception as e:
        return "SQL error: " + str(e)          # send the error back so Claude can fix its SQL
def describe_tables ():
    rows=con.sql(""" select table_name,string_agg(column_name,',')
     from information_schema.columns
      where table_schema='dbt'
       group by table_name """).fetchall()
    return "\n".join(f"dbt.{table}({columns})" for table,columns in rows)
# --- C. the menu ---
tools = [{
    "name": "run_sql",
    "description": "Run one read-only SELECT query on the NYC taxi warehouse and return up to 20 rows.",
    "input_schema": {
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"],
    },
},
    {"name": "describe_tables",
        "description":  "List every table in the NYC taxi warehouse and its columns. Use this first if you are not sure of the names.",
        "input_schema": {
            "type": "object",
            "properties": {},
            
        },  

}]

# --- D. the table list ---
schema = """Tables:
dbt.fact_trips(pickup_zone_id, payment_type_id, pickup_date, trip_distance, fare_amount, tip_amount, total_amount)
dbt.dim_zone(zone_id, zone_name, borough)
dbt.dim_date(date_key, day_name, is_weekend, is_holiday)
dbt.dim_payment(payment_type_id, payment_name)
Joins:
dbt.fact_trips.pickup_zone_id = dbt.dim_zone.zone_id
dbt.fact_trips.pickup_date = dbt.dim_date.date_key
dbt.fact_trips.payment_type_id = dbt.dim_payment.payment_type_id"""

client = anthropic.Anthropic()

# --- E. the agent as a function: ask(question) gives back Claude's answer ---
def ask(question, show_steps=True):
    messages = [{"role": "user", "content": question}]
    for step in range(5):                              # at most 5 rounds (guardrail)
        response = client.messages.create(
            model="claude-opus-5-5",
            max_tokens=2000,
            tools=tools,
            system="You are a data analyst for NYC taxi data. Use describe_tables to see the tables before writing SQL. Answer in at most 5 lines.",
            messages=messages,
        )

        if response.stop_reason != "tool_use":         # F. no more SQL requests -> final answer
            for block in response.content:
                if block.type == "text":
                    return block.text                  # give the answer back
            return "No text in the answer."

        messages.append({"role": "assistant", "content": response.content})   # G. Claude's request

        results = []
        for block in response.content:                 # H. run every SQL Claude asked for
            if block.type == "tool_use":
                if block.name=="describe_tables":
                    result=describe_tables()
                else:
                    sql=block.input["query"]
                    result=run_sql(sql)
                if show_steps:
                    print("Tool:", block.name, block.input)
                    print("Result:", result)
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})

        messages.append({"role": "user", "content": results})                  # I. send the results back
    return "No answer after 5 steps."


# --- J. chat mode: only runs when you run THIS file ---
if __name__ == "__main__":
    while True:
        q = input("\nAsk a question (or type quit): ")
        if q == "quit":
            break
        print("ANSWER:", ask(q))
