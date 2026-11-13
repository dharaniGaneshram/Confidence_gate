def calculate_score_margin(sentences, budget_hit):

    # Exclude neighbor sentences
    valid_sentences = [
        sentence for sentence in sentences
        if not sentence.is_neighbor
    ]

    # Separate selected and rejected
    selected_scores = [
        sentence.score for sentence in valid_sentences
        if sentence.selected
    ]

    rejected_scores = [
        sentence.score for sentence in valid_sentences
        if not sentence.selected
    ]

    # Handle empty groups
    if not selected_scores or not rejected_scores:
        return {
            "score_margin": None,
            "reliable": False,
            "budget_hit": budget_hit,
            "reason": "Selected or rejected group is empty."
        }

    # Calculate boundary margin
    lowest_selected = min(selected_scores)
    highest_rejected = max(rejected_scores)

    margin = lowest_selected - highest_rejected

    # Check budget condition
    if budget_hit:
        return {
            "score_margin": margin,
            "reliable": False,
            "budget_hit": budget_hit,
            "reason": "Budget was reached. Margin should not be trusted."
        }

    return {
        "score_margin": margin,
        "reliable": True,
        "budget_hit": budget_hit,
        "reason": "Margin calculated successfully."
    }