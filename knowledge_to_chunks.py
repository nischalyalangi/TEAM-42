# C:\TEAM-42\knowledge_to_chunks.py
import os
import json
import uuid

# Input folder (clean text)
INPUT_DIR = r"C:\TEAM-42\knowledge_processed"

# Output chunks file (used by FAISS)
OUTPUT_FILE = r"C:\TEAM-42\member2\chunks.json"

CHUNK_SIZE = 200   # words per chunk
OVERLAP = 40       # word overlap for context continuity


def chunk_text(words, size, overlap):
    chunks = []
    start = 0
    while start < len(words):
        end = start + size
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        start = end - overlap
    return chunks


all_chunks = []

for filename in os.listdir(INPUT_DIR):
    if not filename.endswith(".clean.txt"):
        continue

    file_path = os.path.join(INPUT_DIR, filename)

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    words = text.split()
    text_chunks = chunk_text(words, CHUNK_SIZE, OVERLAP)

    for chunk in text_chunks:
        all_chunks.append({
            "id": str(uuid.uuid4()),
            "source": "scikit-learn",
            "topic": "classification",
            "difficulty": "competent",
            "content": chunk
        })

print("Total chunks created:", len(all_chunks))

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_chunks, f, indent=2)

print("chunks.json saved successfully")
