import os
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
import sys # Added for path manipulation in the test block

# --- Pydantic Schema for User Profile (Mock for now) ---
class UserProfile(BaseModel):
    """
    Mock user profile used to simulate adaptive learning scores.
    """
    user_id: str = "learner-123"
    knowledge_score: int = Field(default=55, ge=0, le=100, description="Score from 0 to 100 representing ML theoretical knowledge.")
    coding_score: int = Field(default=70, ge=0, le=100, description="Score from 0 to 100 representing ML coding proficiency.")
    current_topic: str = "Bias-Variance Tradeoff"

# --- Adaptive Logic Functions ---

def get_response_style(score: int) -> tuple[str, str]:
    """
    Determines the explanation depth and the engagement method based on the score.
    Returns: (explanation_style, question_style)
    """
    if score < 40:
        # BEGINNER: Focus on simple explanations (1 paragraph) followed by easy multiple choice.
        explanation_style = (
            "Foundational (Beginner): Provide a simple, 1-2 paragraph definition using analogies. "
            "Explain the 'why' before the 'how'."
        )
        question_style = "Ask a **multiple-choice question (A, B, C)** to assess immediate recall of a basic fact found in the context."
    elif 40 <= score < 80:
        # INTERMEDIATE: Provide a concise, conceptual explanation (2-3 paragraphs) followed by open-ended questions.
        explanation_style = (
            "Competent (Intermediate): Provide a concise, conceptual explanation (2-3 paragraphs). "
            "Focus on mathematical intuition and practical implications. Assume basic familiarity."
        )
        question_style = "Ask a **direct, open-ended 'why' or 'how' question** that requires the learner to apply the concept or reason about its use."
    else: # score >= 80
        # EXPERT: Provide a deeper explanation (3-4 paragraphs) followed by challenging questions.
        explanation_style = (
            "Mastery (Expert): Provide a detailed explanation (3-4 paragraphs). "
            "Be highly technical, use precise mathematical notation, and focus on advanced details, limitations, or alternatives."
        )
        question_style = "Ask a **challenging, critical-thinking question or a design-based prompt** that requires synthesis of multiple concepts."

    return explanation_style, question_style


def build_adaptive_prompt(query: str, context: list[str], profile: UserProfile) -> str:
    """
    Constructs the final, highly specific prompt for the LLM to act as an interactive tutor.
    The response is conditional: First, give an adaptive explanation (1-4 paragraphs), then ask a question.
    """
    # 1. Get the new adaptive style (explanation and question components)
    explanation_style, question_style = get_response_style(profile.knowledge_score)
    
    # 2. Format the retrieved context into a single string
    context_str = "\n---\n".join(context)
    
    # 3. Construct the comprehensive instruction prompt for the new role
    prompt = f"""
    You are the Adaptive Machine Learning Tutor, specialized in the ML curriculum provided in the CONTEXT.
    Your core role is to **EDUCATE AND ENGAGE**.

    --- LEARNER PROFILE ---
    Learner ID: {profile.user_id}
    Knowledge Score: {profile.knowledge_score}/100
    
    --- INSTRUCTIONS ---
    1. **Primary Goal**: Answer the user's implicit query about **{profile.current_topic}** using the provided CONTEXT.
    2. **Explanation Phase**: First, provide a thorough explanation of the topic.
        * **Style**: Strictly follow the Explanation Style: {explanation_style}
        * **Length**: The explanation must be between 1 and 4 paragraphs.
        * **Formatting**: Use Markdown and appropriate LaTeX.
    3. **Engagement Phase**: Immediately after the explanation, shift into Socratic mode and ask a single, relevant question based on the Explanation Style: {question_style}.
    4. **Output Structure**: The response must flow naturally: [Adaptive Explanation] followed by [Adaptive Question].

    --- CONTEXT (Curriculum Source) ---
    {context_str}

    --- USER'S IMPLICIT QUERY ---
    The user is asking about the topic: "{profile.current_topic}"
    
    --- TUTOR RESPONSE START ---
    """
    return prompt

# --- Main Generator Class (Remains the same) ---
class RAGGenerator:
    """
    Handles LLM interaction for final answer generation.
    """
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        # Use GEMINI_API_KEY environment variable if available
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set. Please set it before running.")
        
        # Initialize the LLM
        print(f"Initializing Gemini Model: {model_name}...")
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.3, google_api_key=api_key)
        print("Generator is ready.")

    def generate_response(self, query: str, context: list[str], profile: UserProfile) -> str:
        """
        Generates the LLM response based on context and user profile.
        """
        if not self.llm:
            return "Error: LLM not initialized. Check API Key."
            
        adaptive_prompt = build_adaptive_prompt(query, context, profile)
        
        try:
            # Generate the response
            response = self.llm.invoke(adaptive_prompt)
            return response.content
        except Exception as e:
            # Re-raise or handle the exception more gracefully
            print(f"An error occurred during LLM invocation: {e}")
            return f"An error occurred during LLM invocation. The API may be unavailable or the context was insufficient."


# --- Example Usage (for testing by single handler) ---
if __name__ == "__main__":
    # Add parent directory to path to allow importing retriever.py for testing
    sys.path.append(os.path.dirname(os.path.abspath(__file__))) 
    
    try:
        from retriever import RAGRetriever # Safe import inside the test block
    except ImportError:
        print("ERROR: Could not import RAGRetriever. Ensure retriever.py is saved in the same directory.")
        exit()

    # Initialize components
    # NOTE: You must set the GEMINI_API_KEY environment variable for this block to run.
    try:
        generator = RAGGenerator()
        retriever = RAGRetriever()
    except ValueError as e:
        print(f"Initialization Failed: {e}")
        exit()
    
    if not retriever.is_ready:
        print("Cannot run generator test: Retriever failed to load components.")
        exit()

    print("\n--- Testing Adaptive Generation (Intermediate Style: Explain and Ask Why/How) ---")
    
    # Define a mock user profile with an intermediate score (55)
    intermediate_profile = UserProfile(knowledge_score=55) 
    test_query = "Linear Regression"

    # 1. Retrieve context
    retrieved_context = retriever.retrieve_context(test_query, k=4)
    intermediate_profile.current_topic = test_query # Set topic for the prompt
    
    if retrieved_context:
        # 2. Generate adaptive response
        final_answer = generator.generate_response(test_query, retrieved_context, intermediate_profile)
        
        print(f"\nLearner Score: {intermediate_profile.knowledge_score}/100 (Intermediate)")
        print(f"Query: {test_query}")
        print("\n--- TUTOR RESPONSE (Expected: 2-3 paragraph explanation + 'Why/How' question) ---\n")
        print(final_answer)
        print("\n" + "="*50)
        
    print("\n--- Testing Adaptive Generation (Expert Style: Explain and Ask Critical-Thinking question) ---")

    # Define a mock user profile with an expert score (92)
    expert_profile = UserProfile(knowledge_score=92)
    test_query = "Singular Value Decomposition"
    expert_profile.current_topic = test_query # Set topic for the prompt

    # 1. Retrieve context
    retrieved_context_expert = retriever.retrieve_context(test_query, k=3)
    
    if retrieved_context_expert:
        # 2. Generate adaptive response
        final_answer_expert = generator.generate_response(test_query, retrieved_context_expert, expert_profile)
        
        print(f"\nLearner Score: {expert_profile.knowledge_score}/100 (Expert)")
        print(f"Query: {test_query}")
        print("\n--- TUTOR RESPONSE (Expected: 3-4 paragraph technical explanation + Critical-Thinking question) ---\n")
        print(final_answer_expert)
        print("\n" + "="*50)