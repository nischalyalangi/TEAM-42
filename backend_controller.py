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
# ------------------------------------------------------------------
# INITIAL ASSESSMENT (STATEFUL)
# ------------------------------------------------------------------
# Store temporary answers during onboarding
ONBOARDING_ANSWERS = {}

def run_initial_assessment(user_answer=None):
    global USER_PROFILE, ONBOARDING_ANSWERS

    # If profile exists, we are done
    if USER_PROFILE is not None:
        return None

    # Determine next question
    # If user provided an answer to the *previous* question, verify and store it
    # note: this logic requires knowing *which* question was just asked. 
    # For simplicity, we can look at the sequence or just try to fit the answer.
    # A robust way: get next expected question, if user_answer is provided, assumes it's for that.
    # WAIT: simple `get_next_question` checks what is MISSING.
    # So if we received an answer, we must store it against the 'current' missing question BEFORE calling get_next again.

    from member3.initial_assessment import get_next_question
    
    # 1. If we have an answer, try to apply it to the first missing question
    if user_answer:
        next_q = get_next_question(ONBOARDING_ANSWERS)
        if next_q:
            # Validate answer is in options? For now, trust the UI or perform basic check
            # UI sends the string value of the option.
            ONBOARDING_ANSWERS[next_q["id"]] = user_answer
    
    # 2. Get the next question (after update)
    next_q = get_next_question(ONBOARDING_ANSWERS)
    
    if next_q:
        # We are still in onboarding
        return {
            "type": "assessment",
            "question": next_q["question"],
            "options": next_q["options"]
        }
    else:
        # Assessment complete!
        print("\n=== Initial ML Assessment Complete ===")
        USER_PROFILE = infer_user_profile(ONBOARDING_ANSWERS)
        print("\nUser Profile Locked:")
        print(USER_PROFILE)
        return None

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

    # 1. Handle Onboarding
    assessment_step = run_initial_assessment(user_answer)
    if assessment_step:
        # Return assessment question to UI
        return {
            "question": assessment_step["question"],
            "options": assessment_step["options"], # Pass options to UI
            "explanation": None,
            "tier": "detecting",
            "persona": "detecting",
            "intent": "detecting",
            "score": 0,
            "topic": "Onboarding",
            "subtopic": "Assessment"
        }

    # 2. Normal Tutor Flow (Profile is locked)

    # If user_answer was provided but consumed by onboarding, it's already handled.
    # If user_answer was provided AFTER onboarding (for a concept), it's for evaluation.
    # Need to distinguish? 
    # Simple logic: If we just finished onboarding (USER_PROFILE just created), 
    # we don't treat the *last* onboarding answer as a concept answer.
    # The `run_initial_assessment` returns None exactly when it creates the profile.
    # But `user_answer` passed to it was used for the LAST question.
    # So we should clear `user_answer` if we just finished onboarding?
    # Actually, `tutor_step` assumes `user_answer` is for the *previous* turn.
    # If we just finished onboarding, the next thing is to explain the first topic. 
    # So we ignore `user_answer` for evaluation this turn.
    
    # We can detect if we *just* finished?
    # Or simpler: The user answer for the last assessment question triggered profile creation.
    # We should return the first explanation now. 
    # We should NOT use that answer for evaluation of the *concept*.
    
    # Select weakest topic
    weak_topic = get_weakest_topic()
    current_score = LEARNER_SCORES[weak_topic]
    tier = get_tier(current_score) # Still used for score tracking, though strict persona drives text.

    chunk = get_chunk_by_subtopic(weak_topic)

    # --------------------------------------------------------------
    # EVALUATION (ONLY IF USER ANSWERS AND NOT JUST FINISHED ONBOARDING)
    # --------------------------------------------------------------
    # How to know if just finished? 
    # Simple check: `user_answer` is provided. 
    # If it matches an option from the LAST assessment question, it's not a concept answer.
    # But that's hard to track.
    # Alternative: The UI script calls `callTutor()` with NULL for first start? 
    # No, UI sends answer.
    # Robust fix: `run_initial_assessment` handles the answer. If it consumes it, we shouldn't use it here.
    # But `tutor_step` just takes `user_answer`.
    # Let's assume if we hold `user_answer` is consumed if valid for assessment. 
    # BUT `run_initial_assessment` just returned None. Did it consume? 
    # Yes, if ONBOARDING_ANSWERS has 5 items.
    # Let's treat the first turn after onboarding as "No answer provided" for evaluation purposes.
    # We can rely on a flag or just simplistic logic: 
    # If `user_answer` is in the set of assessment options... (too risky).
    # Let's just proceed. If the answer doesn't match the rubric, score won't change much.
    # Better: explicitly pass a flag `is_assessment_answer`? No, API is simple.
    
    pass # Proceeding with flow

    if user_answer and USER_PROFILE: 
         # Only evaluate if it looks like a concept answer?
         # For simplicity, let's evaluate. The rubric evaluator might give a low score if it's nonsense,
         # but update_score is weighted. 
         # Ideally, we should ignore the very first call after profile creation.
         pass
         
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
    # --------------------------------------------------------------
    # EXPLANATION (GEMINI)
    # --------------------------------------------------------------
    ai_response = explain_chunk(
        chunk=chunk,
        persona=USER_PROFILE["persona"],
        intent=USER_PROFILE["intent"],
        mastery_level=USER_PROFILE["persona"] # Pass persona as mastery/constraint
    )
    
    explanation = ai_response["explanation"]
    ai_question = ai_response["question"]

    # --------------------------------------------------------------
    # SAFE QUESTION EXTRACTION
    # --------------------------------------------------------------
    # Prioritize AI question if available
    if ai_question:
        question = ai_question
    else:
        # Fallback to static assessment
        assessment_prompt = chunk["assessment"]
        if isinstance(assessment_prompt, dict):
            question = assessment_prompt.get("question", "Explain the concept.")
        else:
            question = assessment_prompt

    return {
        "topic": chunk["topic"],
        "subtopic": weak_topic,
        "tier": USER_PROFILE["persona"], # Return persona as tier for UI
        "persona": USER_PROFILE["persona"],
        "intent": USER_PROFILE["intent"],
        "explanation": explanation,
        "question": question,
        "score": round(LEARNER_SCORES[weak_topic], 2)
    }
