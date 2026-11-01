"""AGENT STEP 1: Python talks to Claude.
Run:  .venv/bin/python src/agent_step1.py
Needs ANTHROPIC_API_KEY set in your terminal (export ANTHROPIC_API_KEY="...") - never put the key in this file.


"""
import anthropic

client = anthropic.Anthropic()                 # line A: connects using the key in your terminal

response = client.messages.create(             # line B: send one message to Claude
    model="claude-opus-5-5",                   #   which Claude model
    max_tokens=1000,                           #   max length of the reply
    messages=[{"role": "user", "content": "In one sentence, what is a star schema?"}],
)

for block in response.content:                 # line C: the reply is a list of blocks
    if block.type == "text":                   #   (there can be a "thinking" block first)
        print(block.text)                      #   print only the text block
