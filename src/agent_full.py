import anthropic
import duckdb

# --- A. open the database (read-only) ---
con = duckdb.connect("taxi.duckdb", read_only=True)

# --- B. the hands: run SQL, return up to 20 rows ---
def run_sql(query):
    try:
        rows = con.sql(query).fetchall()
        return str(rows[:20])
    except Exception as e:
        return "SQL error: " + str(e)          # send the error back so Claude can fix its SQL

# --- C. the menu ---
tools = [{
    "name": "run_sql",
    "description": "Run one read-only SELECT query on the NYC taxi warehouse and return up to 20 rows.",
    "input_schema": {
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"],
    },
}]

# --- D. the table list ---
schema = """Tables:
fact_trips(pickup_zone_id, payment_type_id, pickup_date, trip_distance, fare_amount, tip_amount, total_amount)
dim_zone(zone_id, zone_name, borough)
dim_date(date_key, day_name, is_weekend, is_holiday)
dim_payment(payment_type_id, payment_name)
Joins:
fact_trips.pickup_zone_id = dim_zone.zone_id
fact_trips.pickup_date = dim_date.date_key
fact_trips.payment_type_id = dim_payment.payment_type_id"""

client = anthropic.Anthropic()

# --- E. the agent as a function: ask(question) gives back Claude's answer ---
def ask(question, show_steps=True):
    messages = [{"role": "user", "content": question}]
    for step in range(5):                              # at most 5 rounds (guardrail)
        response = client.messages.create(
            model="claude-opus-5-5",
            max_tokens=2000,
            tools=tools,
            system="You are a data analyst for NYC taxi data. Answer in at most 5 lines.\n" + schema,
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
                sql = block.input["query"]
                result = run_sql(sql)
                if show_steps:
                    print("Claude's SQL:", sql)
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
