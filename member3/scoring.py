# scoring.py

def initialize_self_assessment(learner, declared_topic):
    """
    Trust user self-declared knowledge.
    Start testing directly at declared topic.
    """
    learner.current_topic = declared_topic
    return learner


def update_scores(learner, is_correct: bool, difficulty: str):
    """
    Update learner scores based on answer correctness
    """

    learner.attempts += 1

    if is_correct:
        learner.correct_answers += 1

        if difficulty == "easy":
            learner.scores["knowledge"] += 3
        elif difficulty == "medium":
            learner.scores["knowledge"] += 5
            learner.scores["problem_solving"] += 4
        elif difficulty == "hard":
            learner.scores["problem_solving"] += 6
            learner.scores["coding"] += 5

    else:
        learner.scores["knowledge"] -= 2

    # Clamp scores between 0 and 100
    for key in learner.scores:
        learner.scores[key] = max(0, min(100, learner.scores[key]))

    learner.update_tier()
