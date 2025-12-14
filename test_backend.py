import backend_controller
from backend_controller import tutor_step

# Inject default profile to skip assessment (Quick Start)
backend_controller.USER_PROFILE = {
    "persona": "beginner",
    "intent": "Learn ML from scratch", 
    "score": 0.0
}

# First explanation
response = tutor_step()
print("\n=== AI EXPLANATION ===")
print(response["explanation"])

print("\nQUESTION:")
print(response["question"])

user_answer = input("\nYour answer: ")

# Evaluate and continue
response = tutor_step(user_answer)
print("\nUPDATED SCORE:", response["score"])
