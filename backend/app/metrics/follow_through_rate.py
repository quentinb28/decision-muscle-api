def calculate_follow_through_rate(commitments):
    if len(commitments) == 0:
        return {"follow_through_rate": 0}

    completed = sum(1 for c in commitments if c.completed)

    return completed / len(commitments)
