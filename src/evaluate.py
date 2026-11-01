from agent_full import ask
tests=[("which pickup_zone made the most revenue","JFK"),
       ("How may trips were there on 2024-01-01","68127"),
       ("How mant trips happened on weekends","698689"),]
score=0
for question,expected in tests:
    answer=ask(question,show_steps=False)
    correct=expected in answer.replace(",","")
    if correct:
        score=score+1
    print("✅" if correct else "❌", question)
    print("   agent said:", answer[:120])
print(f"Score: {score}/{len(tests)}")