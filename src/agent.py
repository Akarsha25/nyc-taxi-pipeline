import anthropic
import duckdb
con=duckdb.connect("taxi.duckdb",read_only=True)
def run_sql(query):
    rows=con.sql(query).fetchall()
    return str(rows[:20])
print(run_sql("select count(*) from fact_trips"))
tools=[{
"name":"run_sql",
"description":"Run one read_only SELECT Query on the NYC taxi warehous and return up to 20 rows.",
"input_schema":{
    "type":"object",
    "properties":{"query":{"type":"string"}},
    "required":["query"]
},
}]
question = input("Ask a question about NYC taxi data: ")
messages = [{"role": "user", "content": question}]
schema = """Tables:
fact_trips(pickup_zone_id, payment_type_id, pickup_date, trip_distance, fare_amount, tip_amount, total_amount)
dim_zone(zone_id, zone_name, borough)
dim_date(date_key, day_name, is_weekend, is_holiday)
dim_payment(payment_type_id, payment_name)
Joins:
fact_trips.pickup_zone_id = dim_zone.zone_id
fact_trips.pickup_date = dim_date.date_key
fact_trips.payment_type_id = dim_payment.payment_type_id"""
client=anthropic.Anthropic()
response=client.messages.create(
    model="claude-opus-5-5",
    max_tokens=1000,
    tools=tools,
    messages=messages,
    system="You are a data analyst for NYC taxi data. Answer in at most 3 lines.\n" + schema,
         
)

results=[]

for block in response.content:
    if block.type=="tool_use":
        print(response.content)
        print("Result:", run_sql(block.input["query"]))
messages.append({"role":"user","content":results})

