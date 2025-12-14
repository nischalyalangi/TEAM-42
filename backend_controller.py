# backend_controller.py

import os
import json

from member4.gemini_explainer import explain_chunk
from member3.initial_assessment import collect_answers
from member3.profile_rules import infer_user_profile
from member3.ai_evaluator import evaluate_with_rubric
from member3.score_update import update_score

# ------------------------------------------------------------------
# SAFETY CHECK — GEMINI KEY
# ------------------------------------------------------------------

if not os.getenv("GEMINI_API_KEY"):
    raise RuntimeError("GEMINI_API_KEY is not set. Gemini will not work.")

# ------------------------------------------------------------------
# LOAD KNOWLEDGE DATASET
# ------------------------------------------------------------------
DATASET_PATH = "expert_knowledge.json"

with open(DATASET_PATH, "r", encoding="utf-8") as f:
    KNOWLEDGE = json.load(f)

# ------------------------------------------------------------------
# GLOBAL USER STATE (IN-MEMORY)
# ------------------------------------------------------------------
USER_PROFILE = None

# Score per subtopic (0.0 – 1.0)
LEARNER_SCORES = {
    chunk["subtopic"]: 0.3 for chunk in KNOWLEDGE
}

# ------------------------------------------------------------------
# UTILITY FUNCTIONS
# ------------------------------------------------------------------
def get_tier(score: float) -> str:
    if score < 0.4:
        return "foundational"
    elif score < 0.75:
        return "competent"
    return "expert"


def get_weakest_topic():
    return min(LEARNER_SCORES, key=LEARNER_SCORES.get)


def get_chunk_by_subtopic(subtopic):
    return next(c for c in KNOWLEDGE if c["subtopic"] == subtopic)

# ------------------------------------------------------------------
# INITIAL ASSESSMENT (RUN ONCE)
# ------------------------------------------------------------------
def run_initial_assessment():
    global USER_PROFILE

    if USER_PROFILE is None:
        print("\n=== Initial ML Assessment ===")
        answers = collect_answers()
        USER_PROFILE = infer_user_profile(answers)

        print("\nUser Profile Locked:")
        print(USER_PROFILE)

    return USER_PROFILE

# ------------------------------------------------------------------
# MAIN TUTOR STEP
# ------------------------------------------------------------------
def tutor_step(user_answer=None):
    """
    One adaptive tutoring cycle:
    - Pick weakest topic
    - Explain
    - Evaluate (if answer provided)
    - Update score
    """

    run_initial_assessment()

    # Select weakest topic
    weak_topic = get_weakest_topic()
    current_score = LEARNER_SCORES[weak_topic]
    tier = get_tier(current_score)

    chunk = get_chunk_by_subtopic(weak_topic)

    # --------------------------------------------------------------
    # EVALUATION (ONLY IF USER ANSWERS)
    # --------------------------------------------------------------
    if user_answer:
        eval_score = evaluate_with_rubric(
            user_answer,
            chunk["evaluation_rubric"]
        )
        LEARNER_SCORES[weak_topic] = update_score(
            current_score,
            eval_score
        )

    # --------------------------------------------------------------
    # EXPLANATION (GEMINI)
    # --------------------------------------------------------------
    explanation = explain_chunk(
    chunk=chunk,
    persona=USER_PROFILE["persona"],
    intent=USER_PROFILE["intent"],
    mastery_level=tier
)


    # --------------------------------------------------------------
    # SAFE QUESTION EXTRACTION
    # --------------------------------------------------------------
    assessment_prompt = chunk["assessment"]
    if isinstance(assessment_prompt, dict):
        question = assessment_prompt.get("question", "Explain the concept.")
    else:
        question = assessment_prompt

    return {
        "topic": chunk["topic"],
        "subtopic": weak_topic,
        "tier": tier,
        "persona": USER_PROFILE["persona"],
        "intent": USER_PROFILE["intent"],
        "explanation": explanation,
        "question": question,
        "score": round(LEARNER_SCORES[weak_topic], 2)
    }
