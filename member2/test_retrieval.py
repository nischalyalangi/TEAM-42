from member2.step5_faiss_demo import retrieve_context_by_difficulty

query = "What is determinant and rank?"
result = retrieve_context_by_difficulty(
    query=query,
    difficulty="foundational"
)

print("\nRETRIEVED:\n")
print(result)
