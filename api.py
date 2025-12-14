from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import backend_controller
from backend_controller import tutor_step

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserInput(BaseModel):
    answer: str | None = None

@app.post("/api/tutor")
def tutor(input: UserInput):
    return tutor_step(input.answer)

@app.post("/api/reset")
def reset_session():
    # Reset global state for a new session
    backend_controller.USER_PROFILE = None
    # Reset scores (optional, but good for a full restart)
    # Re-initialize scores to default 0.3
    backend_controller.LEARNER_SCORES = {
        k: 0.3 for k in backend_controller.LEARNER_SCORES
    }
    return {"status": "reset"}

# Serve UI files
app.mount("/", StaticFiles(directory="ui", html=True), name="ui")
