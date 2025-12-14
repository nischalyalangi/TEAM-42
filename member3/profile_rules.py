# member3/profile_rules.py

def infer_user_profile(answers):
    score = 0

    # Q1 self-level
    q1 = answers["q1_self_level"]
    if "new" in q1:
        score += 0
    elif "basic" in q1:
        score += 1
    elif "trained" in q1:
        score += 2
    else:
        score += 3

    # Q2 concept check
    if answers["q2_concept_check"] == "Predicting house prices":
        score += 2

    # Q3 math
    q3 = answers["q3_math_level"]
    if "No math" in q3:
        score += 0
    elif "Basic" in q3:
        score += 1
    elif "Linear" in q3:
        score += 2
    else:
        score += 3

    # Q4 practice
    q4 = answers["q4_practical"]
    if "No" in q4:
        score += 0
    elif "libraries" in q4:
        score += 2
    else:
        score += 3

    # Persona mapping
    if score <= 3:
        persona = "beginner"
    elif score <= 6:
        persona = "theory_aware"
    elif score <= 9:
        persona = "practitioner"
    else:
        persona = "advanced"

    return {
        "persona": persona,
        "score": score,
        "intent": answers["q5_intent"]
    }
