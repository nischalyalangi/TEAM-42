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
TOPIC_SELECTED = False

def run_initial_assessment(user_answer=None):
    global USER_PROFILE, ONBOARDING_ANSWERS, TOPIC_SELECTED, LEARNER_SCORES

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
        if USER_PROFILE is None:
            print("\n=== Initial ML Assessment Complete ===")
            USER_PROFILE = infer_user_profile(ONBOARDING_ANSWERS)
            print("\nUser Profile Locked:")
            print(USER_PROFILE)
        
        # --------------------------------------------------------------
        # TOPIC SELECTION (NEW STEP)
        # --------------------------------------------------------------
        # If we just finished assessment or came back with profile but no topic selected
        if not TOPIC_SELECTED:
            # Check if user provided a topic choice
            # We assume user_answer is the choice if we are in this state
            # But wait, if we just created the profile, we haven't asked the question yet?
            # actually, if we just came from `next_q` being None, we just finished Q5.
            # We should immediately return the Topic Question.
            
            # Get available topics
            expert_topics = [k["subtopic"] for k in KNOWLEDGE]
            
            # Check if user_answer matches a topic (Validation)
            if user_answer and any(topic.lower() in user_answer.lower() for topic in expert_topics):
                 # Exact or fuzzy match logic
                 selected = next(t for t in expert_topics if t.lower() in user_answer.lower())
                 print(f"User selected topic: {selected}")
                 
                 # Prioritize this topic: Set score to 0.0 (weakest) so get_weakest_topic picks it
                 LEARNER_SCORES[selected] = 0.0
                 TOPIC_SELECTED = True
                 return None # Proceed to Explanation
            
            # If no valid answer yet, ask the question
            return {
                "type": "assessment", # Keep type assessment to use same UI flow
                "question": f"Assessment complete! You are identified as a {USER_PROFILE['persona']}. What topic are you most excited about?",
                "options": expert_topics
            }
            
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
    
    # Check if answer is a topic selection (heuristic to skip evaluation)
    expert_topics = [k["subtopic"] for k in KNOWLEDGE]
    is_topic_selection = user_answer and any(t.lower() == user_answer.lower() for t in expert_topics)

    # If we just selected a topic, do NOT evaluate the answer as a concept answer
    if is_topic_selection:
        user_answer = None # Clear it so we trigger explanation only

    # Select weakest topic
    weak_topic = get_weakest_topic()
    current_score = LEARNER_SCORES[weak_topic]
    tier = get_tier(current_score) # Still used for score tracking, though strict persona drives text.
    
    # Validation: Ensure chunk exists
    try:
        chunk = get_chunk_by_subtopic(weak_topic)
    except StopIteration:
        # Fallback if somehow weak_topic is invalid
        chunk = KNOWLEDGE[0]
        weak_topic = chunk["subtopic"]

    # --------------------------------------------------------------
    # EVALUATION (ONLY IF USER ANSWERS AND NOT JUST FINISHED ONBOARDING/TOPIC SELECTION)
    # --------------------------------------------------------------
    if user_answer:
        # Only evaluate if we have a valid answer for the *concept*
        # (Though simple rubric evaluation is robust enough for now)
        try:
            eval_score = evaluate_with_rubric(
                user_answer,
                chunk["evaluation_rubric"]
            )
            LEARNER_SCORES[weak_topic] = update_score(
                current_score,
                eval_score
            )
        except Exception as e:
            print(f"Evaluation error: {e}")
            # Do not crash, just proceed

    # Re-fetch score in case it updated
    current_score = LEARNER_SCORES[weak_topic]
    tier = get_tier(current_score)

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
