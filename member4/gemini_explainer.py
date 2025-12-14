import os
import google.generativeai as genai

# --------------------------------------------------
# GEMINI CONFIGURATION (ONLY GEMINI_API_KEY)
# --------------------------------------------------

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY not set.\n"
        "Run this once in PowerShell:\n"
        "setx GEMINI_API_KEY \"your_api_key_here\""
    )

genai.configure(api_key=API_KEY)

# Use a valid, stable Gemini model
model = genai.GenerativeModel("models/gemini-2.5-flash")

# --------------------------------------------------
# PROMPT BUILDER (GUARDRAILED & ADAPTIVE)
# --------------------------------------------------

def build_prompt(chunk, persona, intent, mastery_level):
    """
    Builds a strict, adaptive prompt for Gemini.
    ONE chunk. NO hallucinations.
    """

    return f"""
You are an AI Machine Learning tutor.

STRICT RULES (MANDATORY):
- Use ONLY the knowledge chunk provided below.
- Do NOT add examples, formulas, or concepts not present.
- Do NOT mention sources, datasets, or retrieval.
- Do NOT go beyond the learner's mastery level.
- If something is missing, say: "This concept will be covered later."

LEARNER PROFILE:
Persona: {persona}
Intent: {intent}
Mastery Level: {mastery_level}

KNOWLEDGE CHUNK:
Topic: {chunk["topic"]}
Subtopic: {chunk["subtopic"]}

CONTENT:
{chunk["explanation"]}

TASK:
Explain the above content to the learner.

REQUIREMENTS:
- Match explanation depth to mastery level.
- Use intuition first.
- Be concise and structured.
- Prepare the learner for a short question.

OUTPUT FORMAT (STRICT):
EXPLANATION:
<clear explanation>

CHECKPOINT QUESTION:
<one question based ONLY on this chunk>
"""

# --------------------------------------------------
# MAIN EXPLANATION FUNCTION (CALLED BY BACKEND)
# --------------------------------------------------

def explain_chunk(chunk, persona, intent, mastery_level):
    """
    Calls Gemini using a strictly controlled prompt.
    """

    prompt = build_prompt(
        chunk=chunk,
        persona=persona,
        intent=intent,
        mastery_level=mastery_level
    )

    response = model.generate_content(prompt)
    raw_text = response.text.strip()

    # Simple parsing logic
    explanation_marker = "EXPLANATION:"
    question_marker = "CHECKPOINT QUESTION:"

    explanation = raw_text
    question = None

    if explanation_marker in raw_text and question_marker in raw_text:
        try:
            parts = raw_text.split(question_marker)
            explanation_part = parts[0].replace(explanation_marker, "").strip()
            question_part = parts[1].strip()
            
            explanation = explanation_part
            question = question_part
        except Exception:
            # Fallback if split fails unexpectedly
            pass
            
    return {
        "explanation": explanation,
        "question": question
    }
