# member3/initial_assessment.py

def get_initial_questions():
    return [
        {
            "id": "q1_self_level",
            "question": "Which best describes you?",
            "options": [
                "I'm new to machine learning",
                "I know basic ML concepts",
                "I've trained ML models",
                "I've deployed or researched ML models"
            ]
        },
        {
            "id": "q2_concept_check",
            "question": "Which task is supervised learning best suited for?",
            "options": [
                "Grouping news articles",
                "Predicting house prices",
                "Finding anomalies",
                "Reducing dimensions"
            ],
            "correct": "Predicting house prices"
        },
        {
            "id": "q3_math_level",
            "question": "How comfortable are you with ML mathematics?",
            "options": [
                "No math",
                "Basic algebra & probability",
                "Linear algebra & calculus",
                "Gradients & optimization"
            ]
        },
        {
            "id": "q4_practical",
            "question": "Have you trained ML models yourself?",
            "options": [
                "No",
                "Yes, using libraries",
                "Yes, including tuning & evaluation"
            ]
        },
        {
            "id": "q5_intent",
            "question": "What do you want to use this ML tutor for?",
            "options": [
                "Learn ML from scratch",
                "Interview preparation",
                "Project help",
                "Research / advanced topics",
                "Production / deployment"
            ]
        }
    ]


def collect_answers(simulated_answers=None):
    """
    simulated_answers = dict for testing
    """
    answers = {}

    for q in get_initial_questions():
        qid = q["id"]

        if simulated_answers:
            answers[qid] = simulated_answers[qid]
        else:
            print("\n" + q["question"])
            for idx, opt in enumerate(q["options"]):
                print(f"{idx + 1}. {opt}")

            choice = int(input("Choose option: ")) - 1
            answers[qid] = q["options"][choice]

    return answers
