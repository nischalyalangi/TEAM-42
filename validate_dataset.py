import json

PATH = "expert_knowledge.json"

with open(PATH, encoding="utf-8") as f:
    data = json.load(f)

required_fields = {
    "id", "topic", "subtopic",
    "difficulty", "explanation",
    "assessment", "evaluation_rubric"
}

print(f"Total concepts: {len(data)}")

for i, item in enumerate(data):
    missing = required_fields - item.keys()
    if missing:
        print(f"❌ Item {i} missing fields:", missing)
    else:
        print(f"✅ Item {i} OK:", item["id"])
