# member3/score_update.py
# member3/score_update.py

def update_score(old_score: float, eval_score: float) -> float:
    """
    Smooth score update to avoid sudden jumps
    """
    return round(0.7 * old_score + 0.3 * eval_score, 3)
