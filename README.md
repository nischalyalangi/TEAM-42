# 🎓 Adaptive Machine Learning Tutor (ML-Tutor)

An intelligent, adaptive machine learning tutor that personalizes explanations based on your knowledge level, learning style, and preferred topics. Built with AI-powered content generation and a beautiful modern web interface.

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)

## ✨ Features

- **🎯 Adaptive Learning**: Personalized explanations based on your skill level (Beginner, Theory-Aware, Practitioner, Advanced)
- **🧠 AI-Powered**: Uses Google's Gemini AI to generate contextual explanations and checkpoint questions
- **📊 Smart Profiling**: 5-question assessment to accurately determine your learning persona
- **🎨 Beautiful UI**: Modern dark-themed interface with glassmorphism effects
- **📈 Progress Tracking**: Real-time score tracking and adaptive difficulty adjustment
- **🔄 Re-explain Logic**: Automatically re-explains concepts if you struggle, advances when you succeed
- **🎯 Topic Selection**: Choose what you're most excited to learn about

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Google Gemini API Key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/nischalyalangi/TEAM-42.git
   cd TEAM-42
   ```

2. **Install dependencies**
   ```bash
   pip install fastapi uvicorn google-generativeai
   ```

3. **Configure API Key**
   ```bash
   # Windows (PowerShell)
   $env:GEMINI_API_KEY="your-api-key-here"
   
   # Linux/Mac
   export GEMINI_API_KEY="your-api-key-here"
   ```

4. **Run the application**
   ```bash
   python -m uvicorn api:app --reload --port 8000
   ```

5. **Open browser** → `http://localhost:8000`

## 🏗️ Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **Python 3.11+** - Core programming language
- **Google Gemini AI** - AI model for generating explanations and questions
- **Pydantic** - Data validation using Python type annotations

### Frontend
- **HTML5** - Structure and semantic markup
- **CSS3** - Modern styling with CSS variables, glassmorphism, gradients
- **Vanilla JavaScript** - Client-side logic and API communication
- **Marked.js** - Markdown parsing for rich text rendering
- **Google Fonts (Outfit)** - Typography

### Architecture
- **RESTful API** - Clean API design with `/api/tutor` and `/api/reset` endpoints
- **Stateful Backend** - In-memory session management
- **Modular Design** - Separated concerns (assessment, profiling, evaluation, AI generation)

## 📁 Project Structure

```
TEAM-42/
├── api.py                      # FastAPI application and routes
├── backend_controller.py       # Main tutor logic and state management
├── expert_knowledge.json       # ML curriculum knowledge base
├── member3/
│   ├── initial_assessment.py  # 5-question profiling system
│   ├── profile_rules.py       # Rule-based persona inference
│   ├── ai_evaluator.py        # Answer evaluation using Gemini
│   └── score_update.py        # Adaptive scoring algorithm
├── member4/
│   └── gemini_explainer.py    # AI explanation generation
└── ui/
    ├── index.html             # Main web interface
    ├── style.css              # Modern dark theme styling
    └── script.js              # Client-side logic
```

## 🎮 How It Works

### 1. Initial Assessment
Answer 5 questions:
- Self-reported experience level
- Concept check (supervised learning)
- Math comfort level
- Practical experience
- Learning intent

### 2. Persona Inference
System assigns you one of these personas:
- **Beginner**: Intuition-first, no equations
- **Theory-Aware**: Concepts + light math
- **Practitioner**: Code examples, metrics, trade-offs
- **Advanced**: Proofs, edge cases, research insights
- **Domain User**: Outcomes, interpretation, risks

### 3. Topic Selection
Choose which ML topic you're most excited about (Linear Algebra, Optimization, Neural Networks, etc.)

### 4. Adaptive Learning Loop
1. AI explains the concept at your level
2. Checkpoint question tests understanding
3. Your answer is evaluated
4. Score updates (0.0 - 1.0 scale)
5. If score < 0.4: Re-explain the same topic
6. If score ≥ 0.75: Advance to next topic

## 📊 API Endpoints

### `POST /api/tutor`
Main tutoring endpoint.

**Request:**
```json
{
  "answer": "string or null"
}
```

**Response:**
```json
{
  "question": "What is a vector?",
  "options": ["...", "..."],
  "explanation": "Markdown formatted explanation",
  "persona": "beginner",
  "intent": "Learning from scratch",
  "score": 0.35,
  "topic": "Linear Algebra",
  "subtopic": "Vectors and Matrices"
}
```

### `POST /api/reset`
Resets the session (clears profile and scores).

## 🎨 UI Features

- **Dark Mode**: Deep blue/purple gradients
- **Glassmorphism**: Modern frosted glass effects
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: Persona and score displayed in sidebar
- **Markdown Support**: Rich formatting in AI responses
- **Smooth Animations**: Polished user experience

## 🔧 Configuration

### Knowledge Base
Edit `expert_knowledge.json` to add or modify topics.

### Persona Rules
Modify `member3/profile_rules.py` to adjust persona inference logic.

### AI Prompt
Customize the teaching style in `member4/gemini_explainer.py`.

## 👥 Team

**TEAM-42** - Adaptive ML Tutor Development Team

---

**Made with ❤️ for adaptive learning**
