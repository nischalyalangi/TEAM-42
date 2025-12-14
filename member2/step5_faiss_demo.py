import json
import faiss
import numpy as np
import os
from sentence_transformers import SentenceTransformer

# Resolve dataset path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "expert_knowledge.json")

# Load dataset
with open(DATASET_PATH, encoding="utf-8") as f:
    chunks = json.load(f)

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Extract explanations only
texts = [chunk["explanation"] for chunk in chunks]

# Generate embeddings
embeddings = model.encode(texts, convert_to_numpy=True)
faiss.normalize_L2(embeddings)

# Build FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)
index.add(embeddings)

print(f"[FAISS] Index built with {index.ntotal} chunks")

# Retrieval function
def retrieve_context_by_difficulty(query, difficulty=None, top_k=5):
    query_embedding = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_embedding)

    scores, indices = index.search(query_embedding, top_k)

    for idx in indices[0]:
        if difficulty is None or chunks[idx]["difficulty"] == difficulty:
            return chunks[idx]

    return chunks[indices[0][0]]


# Standalone test
if __name__ == "__main__":
    test = retrieve_context_by_difficulty(
        query="What is matrix rank?",
        difficulty="foundational"
    )

    print("\n[TEST RETRIEVAL]")
    print("ID:", test["id"])
    print("Topic:", test["topic"])
    print("Explanation:", test["explanation"][:200], "...")
