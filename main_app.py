import uvicorn
import time
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Depends, HTTPException, Request 
from pydantic import BaseModel, Field
from typing import Annotated
import os # Ensure os is imported for API key handling

# Import the core RAG components
try:
    from retriever import RAGRetriever
    from generator import RAGGenerator, UserProfile
except ImportError as e:
    print(f"CRITICAL ERROR: Failed to import core RAG components. Ensure retriever.py and generator.py are in the same folder.")
    print(f"Details: {e}")
    exit()

# --- 1. FastAPI Setup ---
app = FastAPI(
    title="Adaptive ML Tutor RAG API",
    version="1.0.0",
    description="A Retrieval-Augmented Generation API for the Machine Learning Curriculum.",
)

# Initialize Jinja2Templates for HTML rendering
# Assuming you have a 'templates' folder with 'chat_ui.html'
templates = Jinja2Templates(directory="templates") 

# --- GLOBAL STATE MANAGEMENT (for the interactive dialogue) ---
USER_ID = "fastapi_user" # Hardcoded ID for single-user session
USER_STATE = {
    USER_ID: {
        "knowledge_score": 50,          # Starting score
        "last_question": None,          # Tracks the dialogue state (e.g., "initial_assessment", "concept_question")
        "current_topic": "General ML"   # Stores the last topic the user asked about
    }
}
# -----------------------------

# --- 2. Input/Output Schemas (Simplified for Chat UI) ---
class QueryInput(BaseModel):
    """Schema for the incoming user request from the chat UI."""
    query: str = Field(..., description="The user's question or answer.")

class ResponseOutput(BaseModel):
    """Schema for the final API response (only the answer)."""
    answer: str = Field(..., description="The adaptive, curriculum-grounded response from the LLM.")


# --- 3. Component Initialization (Dependency Injection) ---

rag_retriever = None
rag_generator = None
rag_retriever_is_ready = False

@app.on_event("startup")
def load_rag_components():
    global rag_retriever
    global rag_generator
    global rag_retriever_is_ready
    
    try:
        print("--- RAG Retriever: Loading Components ---")
        # Initialize RAG components
        rag_retriever = RAGRetriever()
        rag_generator = RAGGenerator()
        
        if not rag_retriever.is_ready:
            # This is critical, if the retriever failed to load the index/chunks/model
            raise RuntimeError("Retriever initialization failed. Check index files and embeddings model.")
        
        rag_retriever_is_ready = True
        print("RAG System is initialized and ready.")
        
    except ValueError as e:
        # Handles the case where GEMINI_API_KEY is missing (caught in RAGGenerator __init__)
        print(f"Startup Error: {e}")
        raise RuntimeError("Application startup failed due to missing GEMINI_API_KEY.") from e
    except RuntimeError as e:
        print(f"Startup Error: {e}")
        raise RuntimeError("Application startup failed due to RAG component error.") from e
    except Exception as e:
        print(f"Unexpected Startup Error: {e}")
        raise RuntimeError(f"Application failed to start: {e}")

# Dependency function to get the components
def get_rag_system():
    if not rag_retriever_is_ready:
        raise HTTPException(status_code=503, detail="RAG system not initialized. Check server logs.")
    return rag_retriever, rag_generator

# Use Annotated for cleaner dependency injection
RAGSystem = Annotated[tuple[RAGRetriever, RAGGenerator], Depends(get_rag_system)]


# --- 4. API Endpoint (UI Renderer - Handles GET /) ---
@app.get("/", response_class=HTMLResponse, tags=["UI"])
async def serve_ui(request: Request):
    """Serves the main HTML UI (chat_ui.html) for the Adaptive Tutor."""
    # Note: 'templates' folder must exist and contain 'chat_ui.html'
    return templates.TemplateResponse("chat_ui.html", {"request": request})


# --- 5. API Endpoint (RAG Logic - Handles POST /ask) ---
@app.post("/ask", response_model=ResponseOutput, tags=["Adaptive Tutor"])
async def ask_adaptive_question(
    input_data: QueryInput,
    rag_system: RAGSystem
):
    retriever, generator = rag_system
    user_id = USER_ID

    # 1. Retrieve current user profile and state
    current_state = USER_STATE.get(user_id, {"knowledge_score": 50, "last_question": None, "current_topic": "General ML"})
    current_score = current_state["knowledge_score"]
    
    query = input_data.query.strip()
    query_lower = query.lower()
    feedback = ""
    
    # --- DIALOGUE STATE CHECK: INITIAL GREETING/ASSESSMENT ---
    if current_state.get("last_question") is None or "learn machine learning" in query_lower or "start learning" in query_lower:
        initial_prompt = (
            "Hello! I'm your Adaptive ML Tutor. "
            "To personalize our session, let's start with a general assessment. "
            "On a scale of 0 to 100, **how familiar do you feel with foundational Machine Learning concepts?** "
            "(0 being beginner, 100 being expert. Please enter a number.)"
        )
        current_state["last_question"] = "initial_assessment"
        USER_STATE[user_id] = current_state
        return ResponseOutput(answer=initial_prompt)

    # --- DIALOGUE STATE CHECK: PROCESSING INITIAL SCORE ---
    if current_state.get("last_question") == "initial_assessment" and query.isdigit():
        new_score = int(query)
        current_score = max(0, min(100, new_score)) 
        
        current_state["knowledge_score"] = current_score
        current_state["last_question"] = "topic_selection"
        USER_STATE[user_id] = current_state
        
        topic_prompt = (
            f"Thank you! I've set your initial knowledge level to **{current_score}/100**. "
            "Now, what specific topic within Machine Learning are you most interested in exploring right now? "
            "*(e.g., 'Linear Regression', 'Bias-Variance Tradeoff')*"
        )
        return ResponseOutput(answer=topic_prompt)

    # --- DIALOGUE STATE CHECK: USER IS ANSWERING A CONCEPT QUESTION ---
    if current_state.get("last_question") == "concept_question":
        # Simulate Score Adjustment based on answer length/complexity
        if len(query.split()) >= 5 and "i don't know" not in query_lower: 
             current_score = min(100, current_score + 5) 
             feedback = "That's a thoughtful response! Your knowledge is increasing. Let's build on that."
        else:
             current_score = max(0, current_score - 5) 
             feedback = "Interesting point! We can clarify that. Let's move to the next concept to solidify your understanding."
        
        current_state["knowledge_score"] = current_score
        current_state["last_question"] = "ready_for_next_question"
        USER_STATE[user_id] = current_state
        # Fall through to the concept question logic below to continue the dialogue.

    # --- DIALOGUE STATE CHECK: ASKING A NEW/FOLLOW-UP CONCEPT QUESTION (The main loop) ---
    
    # If the user is asking a new topic (not just answering), update the current_topic
    if current_state.get("last_question") == "topic_selection":
        current_state["current_topic"] = query 
        USER_STATE[user_id] = current_state

    # 1. Prepare User Profile
    user_profile = UserProfile(
        user_id=user_id,
        knowledge_score=current_score,
        current_topic=current_state["current_topic"]
    )

    # 2. Retrieval Step 
    topic_for_search = current_state["current_topic"]
    context_chunks = retriever.retrieve_context(topic_for_search, k=4)
    
    if not context_chunks:
        current_state["last_question"] = "topic_selection"
        USER_STATE[user_id] = current_state
        return ResponseOutput(answer=f"I couldn't find relevant curriculum information on '{topic_for_search}'. Please choose a core ML concept from the curriculum.")

    # 3. Generation Step (The LLM is now instructed to EXPLAIN AND ASK)
    
    # Prepend feedback if this is a follow-up answer
    prefix = f"{feedback}\n\n" if current_state.get("last_question") == "ready_for_next_question" else ""
    
    # We pass the topic to the generator, which is instructed to explain it, then ask a question.
    final_response_with_question = generator.generate_response(
        f"Provide an adaptive explanation and ask a question about: {user_profile.current_topic}", 
        context_chunks, 
        user_profile
    )
    
    # 4. Update state to expect an answer
    current_state["last_question"] = "concept_question"
    USER_STATE[user_id] = current_state
    
    # 5. Return the explanation and question
    return ResponseOutput(answer=prefix + final_response_with_question)


# --- 6. Application Run Command ---
if __name__ == "__main__":
    # Ensure all components are loaded if running directly via 'python main_app.py'
    try:
        if not rag_retriever_is_ready:
            load_rag_components() 
    except RuntimeError as e:
        print(f"\n--- SERVER START ABORTED --- Error: {e}")
        exit()
        
    print("\n--- RAG API STARTING ---")
    
    uvicorn.run(
        app, # Pass the app object directly
        host="127.0.0.1", 
        port=8000, 
        log_level="info", 
        reload=False
    )