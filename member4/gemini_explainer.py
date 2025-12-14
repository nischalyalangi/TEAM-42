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
You are an adaptive AI tutor focused ONLY on Machine Learning.

Your primary objective is to:
1. Explain the concept based strictly on the user's inferred profile.
2. Adapt all explanations to the PREDEFINED USER PERSONA below.

STRICT RULES:
- Do NOT discuss non-ML topics.
- Do NOT over-question the user.
- Do NOT assume expertise without validation.
- Do NOT explain advanced math unless the profile allows it.
- Be concise, precise, and technically correct.

USER PROFILE (INFERRED):
Persona: {persona} (Constraint: {mastery_level})
Intent: {intent}

KNOWLEDGE CHUNK:
Topic: {chunk["topic"]}
Subtopic: {chunk["subtopic"]}

CONTENT:
{chunk["explanation"]}

ADAPTATION RULES:
- Beginner → intuition, visuals (described), no equations.
- Theory-Aware → concepts + light math.
- Practitioner → code, metrics, trade-offs.
- Advanced → proofs, edge cases, research insights.
- Domain User → outcomes, interpretation, risks.

TASK:
Explain the content above to the user, strictly following the Adaptation Rules for their persona.

OUTPUT FORMAT (STRICT):
EXPLANATION:
<Adaptive explanation>

CHECKPOINT QUESTION:
<One follow-up question based ONLY on this chunk, adapted to the persona>
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
