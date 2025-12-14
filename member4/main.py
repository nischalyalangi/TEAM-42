from member2.step5_faiss_demo import retrieve_context_by_difficulty
from member4.gemini_explainer import explain_chunk
from member3.initial_assessment import run_initial_assessment
from member3.ai_evaluator import evaluate_with_rubric
from member3.score_update import update_score
import json

with open("expert_knowledge.json") as f:
    chunks = json.load(f)

learner_scores = run_initial_assessment(chunks)

while True:
    weak_concept = min(learner_scores, key=learner_scores.get)
    chunk = next(c for c in chunks if c["subtopic"] == weak_concept)

    tier = (
        "foundational" if learner_scores[weak_concept] < 0.4
        else "competent" if learner_scores[weak_concept] < 0.75
        else "mastery"
    )

    explanation = explain_chunk(chunk, tier)
    print("\n=== AI EXPLANATION ===")
    print(explanation)

    print("\nFollow-up Question:")
    print(chunk["assessment"]["question"])
    user_answer = input("Your answer: ")

    score = evaluate_with_rubric(user_answer, chunk["evaluation_rubric"])
    learner_scores[weak_concept] = update_score(
        learner_scores[weak_concept], score
    )

    print("\nUpdated Score:", learner_scores[weak_concept])

    if learner_scores[weak_concept] >= 0.9:
        print(f"\n🎉 You mastered {weak_concept}!")
        break
