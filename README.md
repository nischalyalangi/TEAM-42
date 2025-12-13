# Adaptive Machine Learning Tutor (ML-Tutor)

## 1. Problem Statement

The current landscape of online machine learning education is largely static, offering the same fixed curriculum regardless of the learner's existing knowledge, coding proficiency, or problem-solving capability. This leads to inefficient learning pathways, where advanced learners are bored by foundational material, and beginners are quickly overwhelmed by complex concepts.

The core problem this project addresses is the need for **personalized, adaptive instruction** in Machine Learning. Our goal is to create an AI-powered tutor that:

1.  **Accurately Assesses** a user's current knowledge and skills across multiple dimensions (knowledge, coding, problem-solving, deployment, etc.), scoring them out of 100.
2.  **Adaptively Explains** complex ML topics using a tone and depth (foundational, competent, expert) dynamically determined by the user's score profile.
3.  **Intelligently Assesses** mastery by asking targeted questions, checking the user's understanding of prerequisites, and moving them through the curriculum only when true mastery is demonstrated.

## 2. Data Link (Curriculum Source)

The entire curriculum structure and educational content are derived from a single, exhaustive source, which serves as the project's **Expert Model**.

- **Source File:** `Machine-learning-all-topics.txt`
- [cite_start]**Content:** This file contains a comprehensive, end-to-end Machine Learning roadmap, covering everything from core mathematical foundations (Linear Algebra, Probability, Calculus) [cite: 1] [cite_start]and Python programming [cite: 3] [cite_start]to core algorithms (Supervised [cite: 6][cite_start], Unsupervised [cite: 6][cite_start]), Deep Learning [cite: 16][cite_start], Model Evaluation [cite: 15][cite_start], Deployment, and MLOps[cite: 17].
- **Role:** This structured content is ingested into the Vector Database to provide the Retrieval-Augmented Generation (RAG) system with a factual and domain-specific knowledge base for generating explanations.

## 3. System Design and Architecture

The ML-Tutor is structured around a three-tier model, leveraging modern LLM and data engineering techniques.

### Core Adaptive Architecture

1.  **Expert Model:** The structured curriculum (from `Machine-learning-all-topics.txt`), mapping topics and their prerequisites. Stored in PostgreSQL.
2.  **Learner Model:** A relational database storing the user's dynamic profile, including all assessed scores (knowledge, coding, problem-solving, etc.), current topic, and historical performance. Stored in PostgreSQL.
3.  **Tutor Logic (Orchestrator):** The application layer that dictates the flow:
    - **Assessment:** If a user's score is below a threshold (e.g., <40%), trigger a clear, foundational explanation. If the score is high (e.g., >80%), trigger a deep, complex question.
    - **Generation:** Uses the user's profile to inject specific style and difficulty instructions into the LLM prompt.

### Tech Stack

| Component             | Technology                            | Rationale                                                                                                                                       |
| :-------------------- | :------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------- |
| **Core Framework**    | Python (FastAPI)                      | High-performance, asynchronous backend for handling API requests and business logic.                                                            |
| **AI Core**           | LLM (e.g., Gemini, GPT, Llama)        | Handles conversational intelligence, content generation, and question creation.                                                                 |
| **RAG Orchestration** | LangChain / LlamaIndex                | Manages the complex Retrieval-Augmented Generation pipeline.                                                                                    |
| **Knowledge Storage** | Vector Database (FAISS for prototype) | Stores semantic embeddings of the curriculum for fast, context-aware retrieval.                                                                 |
| **Data Storage**      | PostgreSQL                            | Robust relational database for managing the structured Expert Model (topic hierarchy) and the dynamic Learner Model (user profiles and scores). |
| **RAG Quality**       | Re-ranking Model (e.g., Cohere)       | Used to improve retrieval accuracy by filtering the most relevant chunks before generation.                                                     |

## 4. Key Assumptions and Design Decisions

### A. Foundational Assumptions

- **Curriculum Completeness:** We assume the content provided in `Machine-learning-all-topics.txt` is the definitive and exhaustive knowledge base for the project. The bot will not teach concepts outside of this file.
- **LLM Reliability:** We assume the chosen LLM can reliably follow complex, multi-part prompt instructions for adapting explanation style and generating questions with consistent difficulty.
- **Initial Self-Assessment:** The learning process starts by trusting the user's initial self-assessment of the topic they know up to (e.g., "I know until Classification"). This sets the first testing milestone.

### B. Adaptive Logic Design Decisions

- **Multi-Dimensional Scoring:** User assessment is scaled out of 100 for multiple traits (knowledge, coding, problem-solving, deployment) to create a nuanced profile, rather than a single knowledge metric.
- **Grading Tiers for Adaptation:** The system uses three primary score thresholds to define the adaptive style:
  - **Below 40% (Foundational):** Explain concepts very clearly, using simple language. Ask easy, definitional questions.
  - **40% - 80% (Competent):** Explain concisely, filling gaps. Ask medium-difficulty application or comparison questions.
  - **Above 80% (Mastery):** Explain short, technical details. Ask deep, complex, or system-design questions.
- **Prerequisite Check:** Upon a user stating their current knowledge, the system _assumes_ they know all prerequisites and immediately jumps to testing the stated topic (e.g., if a user knows Classification, the first test is on Classification, not Linear Regression). The user is prompted to ask for a review if needed.
