# member3/ai_evaluator.py

def evaluate_with_rubric(user_answer: str, rubric: dict) -> float:
    """
    Evaluates a user answer against a rubric.
    Returns a score between 0.0 and 1.0
    """

    if not user_answer or not rubric:
        return 0.0

    answer = user_answer.lower()

    # Simple heuristic-based evaluation (offline-safe)
    if len(answer) < 10:
        return 0.2

    # Keyword matching from rubric
    score = 0.0
    checks = 0

    for level, description in rubric.items():
        checks += 1
        keywords = description.lower().split()

        if any(word in answer for word in keywords):
            score += 1

    if checks == 0:
        return 0.3

    # Normalize to 0–1
    return min(score / checks, 1.0)
