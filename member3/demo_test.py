# demo_test.py

from learner_model import LearnerProfile
from scoring import initialize_self_assessment, update_scores
from assessment import get_adaptive_questions

# Create learner
learner = LearnerProfile(user_id="demo_user", current_topic="")

# Self assessment
initialize_self_assessment(learner, "Classification")

print("Initial Tier:", learner.tier)

# Get questions
questions = get_adaptive_questions("Classification", learner.tier)

# Simulate answering first question correctly
q = questions[0]
update_scores(learner, is_correct=True, difficulty=q["difficulty"])

print("Updated Scores:", learner.scores)
print("Updated Tier:", learner.tier)
