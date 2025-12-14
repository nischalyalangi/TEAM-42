import json

data = json.load(open("expert_knowledge.json"))

for c in data:
    assert all(k in c for k in [
        "id", "topic", "subtopic", "difficulty",
        "explanation", "assessment", "evaluation_rubric"
    ])
