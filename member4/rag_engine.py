# rag_engine.py

def generate_explanation(topic, style):
    explanations = {
        "foundational": f"{topic} is a basic ML task where we assign labels to data.",
        "competent": f"{topic} involves supervised learning algorithms that map inputs to discrete outputs.",
        "mastery": f"{topic} models decision boundaries in feature space using probabilistic or margin-based approaches."
    }

    return explanations.get(style, "")
