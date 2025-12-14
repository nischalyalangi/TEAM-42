from member2.step5_faiss_demo import retrieve_context_by_difficulty

queries = [
    "Explain determinant and rank",
    "What is gradient descent?",
    "How do we evaluate a model?"
]

for q in queries:
    result = retrieve_context_by_difficulty(q, difficulty="foundational")
    print("\nQUERY:", q)
    print("RETRIEVED ID:", result["id"])
    print("EXPLANATION:", result["explanation"][:150], "...")
