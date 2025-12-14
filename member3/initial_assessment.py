# member3/initial_assessment.py

def get_initial_questions():
    return [
        {
            "id": "q1_self_level",
            "question": "Which best describes you?",
            "options": [
                "New to machine learning",
                "Know basic ML concepts",
                "Have trained ML models",
                "Have deployed or researched ML models"
            ]
        },
        {
            "id": "q2_concept_check",
            "question": "Which task is supervised learning best suited for?",
            "options": [
                "Grouping news articles by similarity",
                "Predicting house prices from past sales",
                "Detecting anomalies in network traffic",
                "Reducing dimensionality"
            ],
            "correct": "Predicting house prices from past sales"
        },
        {
            "id": "q3_math_level",
            "question": "How comfortable are you with the following? (Select highest)",
            "options": [
                "None of the above",
                "Probability & statistics",
                "Linear algebra",
                "Calculus (gradients)"
            ]
        },
        {
            "id": "q4_practical",
            "question": "Have you ever trained a model yourself?",
            "options": [
                "No",
                "Yes, using ML libraries",
                "Yes, including tuning and evaluation"
            ]
        },
        {
            "id": "q5_intent",
            "question": "What do you want to use this ML tutor for?",
            "options": [
                "Learning from scratch",
                "Interview prep",
                "Project help",
                "Research / advanced topics",
                "Production / deployment"
            ]
        }
    ]


def get_next_question(current_answers):
    """
    Returns the next question object that hasn't been answered yet.
    Returns None if all are answered.
    """
    questions = get_initial_questions()
    for q in questions:
        if q["id"] not in current_answers:
            return q
    return None

def collect_answers(simulated_answers=None):
    """
    Legacy support for CLI testing if needed, or strictly deprecated.
    For now, keeping it simple or removing if main loop changes.
    Let's keep a simplified version that uses the new logic for CLI compatibility.
    """
    answers = {}
    if simulated_answers:
        return simulated_answers

    # Interactive CLI loop (blocking)
    while True:
        q = get_next_question(answers)
        if not q:
            break
        
        print("\n" + q["question"])
        for idx, opt in enumerate(q["options"]):
            print(f"{idx + 1}. {opt}")
        
        try:
            choice = int(input("Choose option: ")) - 1
            if 0 <= choice < len(q["options"]):
                answers[q["id"]] = q["options"][choice]
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input.")

    return answers
