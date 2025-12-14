# learner_model.py

class LearnerProfile:
    def __init__(self, user_id: str, current_topic: str):
        self.user_id = user_id
        self.current_topic = current_topic

        # Multi-dimensional scores (0–100)
        self.scores = {
            "knowledge": 50,
            "coding": 40,
            "problem_solving": 45,
            "deployment": 30
        }

        self.attempts = 0
        self.correct_answers = 0
        self.tier = self.calculate_tier()

    def calculate_tier(self):
        avg_score = sum(self.scores.values()) / len(self.scores)

        if avg_score < 40:
            return "foundational"
        elif avg_score <= 80:
            return "competent"
        else:
            return "mastery"

    def update_tier(self):
        self.tier = self.calculate_tier()
