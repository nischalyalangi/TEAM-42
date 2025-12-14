import json

# Load chunks.json
with open("chunks.json", "r") as f:
    chunks = json.load(f)

# Basic sanity checks
print("Total chunks loaded:", len(chunks))
print("\nFirst chunk preview:\n")
print(chunks[0])
