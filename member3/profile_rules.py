# member3/profile_rules.py

def infer_user_profile(answers):
    # Rule-based logic from PRD
    # Priorities: 
    # 1. Domain User (Intent)
    # 2. Practitioner/Advanced (Experience)
    # 3. Theory-Aware vs Beginner (Concept correctness + Math)

    q2_concept = answers.get("q2_concept_check", "")
    q3_math = answers.get("q3_math_level", "")
    q4_practice = answers.get("q4_practical", "")
    q5_intent = answers.get("q5_intent", "")

    # 1. Domain User
    if "Production" in q5_intent or "Project" in q5_intent:
        # Check if they are actually practitioners first
        if "tuning" not in q4_practice and "deployed" not in q4_practice:
             # Just a user of ML outputs? Refine logic if needed, 
             # but PRD implies "Uses ML outputs" -> Domain User.
             # However, PRD Priority says Q2/Q4 override. 
             pass # Let's stick to the core logic below first.

    persona = "beginner" # Default

    # Logic Tree
    is_concept_correct = "Predicting house prices" in q2_concept
    has_math = "Calculus" in q3_math or "Linear" in q3_math or "Probability" in q3_math
    has_practice = "tuning" in q4_practice
    has_deployment = "deployed" in answers.get("q1_self_level", "") # Access Q1 for advanced check

    if "Research" in q5_intent or has_deployment:
        persona = "advanced"
    elif "Production" in q5_intent and has_practice:
        persona = "practitioner"
    elif has_practice:
        persona = "practitioner"
    elif is_concept_correct and has_math:
        persona = "theory_aware"
    elif is_concept_correct and not has_math:
        # Still effectively beginner/domain user side, but let's call them...
        # PRD says "Concept wrong + no math -> Beginner".
        # If Concept Right + No Math -> Maybe just "Beginner" with good intuition?
        persona = "beginner" 
    else:
        # Concept wrong
        persona = "beginner"
    
    # Special case for "Domain User" if they strictly want to use it for work but have no deep skills
    if "Project" in q5_intent and persona == "beginner":
        persona = "domain_user"

    return {
        "persona": persona,
        "score": 0, # Legacy, can remove or keep for compatibility
        "intent": q5_intent
    }
