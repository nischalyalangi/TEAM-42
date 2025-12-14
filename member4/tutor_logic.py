# tutor_logic.py

def decide_action(learner):
    """
    Decide what to do next based on learner tier
    """
    if learner.tier == "foundational":
        return "explain_simple"
    elif learner.tier == "competent":
        return "explain_normal"
    else:
        return "ask_advanced"
