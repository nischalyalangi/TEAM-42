from backend_controller import tutor_step

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
