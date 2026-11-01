"""WATCH the blocks in Claude's reply, round by round.
Run:  .venv/bin/python src/watch_blocks.py
"""
from agent_full import client, tools, schema, run_sql

messages = [{"role": "user", "content": "which pickup zone made the most revenue?"}]

for round_number in range(1, 4):
    response = client.messages.create(
        model="claude-opus-5-5", max_tokens=2000, tools=tools,
        system="You are a data analyst for NYC taxi data. Answer in at most 3 lines.\n" + schema,
        messages=messages,
    )
    print(f"\n========== ROUND {round_number}: Claude's reply has {len(response.content)} blocks ==========")
    for i, block in enumerate(response.content, start=1):
        print(f"block {i}:  block.type = {block.type!r}")
        if block.type == "tool_use":
            print(f"          block.input = {block.input}")
        if block.type == "text":
            print(f"          block.text  = {block.text!r}")

    if response.stop_reason != "tool_use":
        print("\n-> Claude is finished. That text block is the answer.")
        break

    messages.append({"role": "assistant", "content": response.content})
    results = []
    for block in response.content:
        if block.type == "tool_use":
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": run_sql(block.input["query"])})
    messages.append({"role": "user", "content": results})
    print("\n-> our code ran the SQL and sent the result back to Claude")
