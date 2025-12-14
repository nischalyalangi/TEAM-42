#C:\TEAM-42\api.py
from fastapi import FastAPI
from pydantic import BaseModel
from backend_controller import tutor_step

app = FastAPI()

class UserInput(BaseModel):
    answer: str | None = None

@app.post("/tutor")
def tutor(input: UserInput):
    return tutor_step(input.answer)
