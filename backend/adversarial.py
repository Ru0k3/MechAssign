def choose_request(request_a, request_b):
    """2-ply minimax: dispatcher (MAX) picks who to serve first; the MIN
    layer represents worst-case urgency escalation for whoever waits."""
    ESCALATION = 3  # how much worse urgency can get while a job waits

    alpha = float("-inf")
    options = [
        ("serve_a_first", request_a, request_b),
        ("serve_b_first", request_b, request_a),
    ]

    best_choice = None
    best_value = float("-inf")
    pruned = 0

    for label, served, waiting in options:
        outcomes = [waiting["urgency"], waiting["urgency"] + ESCALATION]
        min_value = float("inf")
        for outcome_urgency in outcomes:
            value = served["urgency"] - outcome_urgency
            if value < min_value:
                min_value = value
            if min_value <= alpha:
                pruned += 1
                break

        if min_value > best_value:
            best_value = min_value
            best_choice = label
        alpha = max(alpha, best_value)

    winner = request_a if best_choice == "serve_a_first" else request_b
    return {"winner": winner, "value": best_value, "nodes_pruned": pruned}