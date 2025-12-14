# STEP 3: Generate embeddings from chunks.json

import json
import numpy as np
from sentence_transformers import SentenceTransformer

# 1. Load chunks.json
with open("chunks.json", "r") as f:
    chunks = json.load(f)

print("Chunks loaded:", len(chunks))

# 2. Extract text content only
texts = [chunk["content"] for chunk in chunks]

print("Texts extracted:", len(texts))

# 3. Load embedding model
print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded successfully.")

# 4. Generate embeddings
print("Generating embeddings...")
embeddings = model.encode(texts, convert_to_numpy=True)

# 5. Verify embeddings
print("Embeddings generated.")
print("Embedding shape:", embeddings.shape)
print("Embedding type:", type(embeddings))
