# MEMBER 1 - STEP 1 + STEP 2
# Tutor Orchestrator with Adaptive Prompt

import sys

# Add Member-2 folder to Python path
sys.path.append(r"C:\TEAM-42\member2")

# Import adaptive retrieval function FIRST
from step5_faiss_demo import retrieve_context_by_difficulty

print("Member-2 FAISS retrieval imported successfully.")

# --------------------------------------------------
# STEP 1 TEST: Retrieval
# --------------------------------------------------
query = "What is classification?"
context = retrieve_context_by_difficulty(query, difficulty="foundational")

print("\nRetrieved Context:")
print(context)

# --------------------------------------------------
# STEP 2: Adaptive Prompt Builder
# --------------------------------------------------
def build_adaptive_prompt(user_query, difficulty="foundational"):
    """
    Builds an adaptive tutor prompt using:
    - Grounded context from FAISS
    - Difficulty-aware instruction
    - Hallucination protection
    """

    context = retrieve_context_by_difficulty(
        user_query,
        difficulty=difficulty
    )

    prompt = f"""
You are an AI Machine Learning tutor.

STRICT RULES:
- Answer ONLY using the provided context.
- If the answer is not present in the context, say:
  "I do not have this information in my curriculum."

TEACHING LEVEL: {difficulty}

CONTEXT:
{context}

STUDENT QUESTION:
{user_query}

ANSWER:
"""
    return prompt

# --------------------------------------------------
# STEP 2 TEST
# --------------------------------------------------
print("\n=== ADAPTIVE PROMPT TEST ===")

test_prompt = build_adaptive_prompt(
    "How do we evaluate classification models?",
    difficulty="competent"
)

print(test_prompt)

# --------------------------------------------------
# STEP 3: Simulated LLM (NO API)
# --------------------------------------------------

def simulated_llm(prompt, difficulty="foundational"):
    """
    Simulates LLM response for demo purposes.
    No external API calls.
    """

    print("\n=== PROMPT SENT TO LLM ===")
    print(prompt)

    # Deterministic safe responses based on difficulty
    if difficulty == "foundational":
        return (
            "Classification assigns input data into predefined categories. "
            "It is evaluated using metrics such as accuracy, precision, recall, "
            "and F1-score."
        )

    if difficulty == "competent":
        return (
            "Classification models are evaluated using accuracy, precision, recall, "
            "and F1-score. Accuracy measures overall correctness, precision measures "
            "the correctness of positive predictions, and recall measures the ability "
            "to identify actual positives."
        )

    return "I do not have this information in my curriculum."


# --------------------------------------------------
# END-TO-END DEMO (NO API)
# --------------------------------------------------

print("\n=== END-TO-END TUTOR DEMO ===")

user_question = "How do we evaluate classification models?"
user_level = "competent"  # change to foundational / competent

adaptive_prompt = build_adaptive_prompt(
    user_question,
    difficulty=user_level
)

final_answer = simulated_llm(
    adaptive_prompt,
    difficulty=user_level
)

print("\n=== FINAL TUTOR RESPONSE ===")
print(final_answer)
