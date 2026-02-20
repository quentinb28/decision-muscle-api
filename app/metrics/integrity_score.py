def calculate_integrity_score(followups):
    if len(followups) == 0:
        return 0

    completed = sum(1 for f in followups if f.completed)

    return completed / len(followups)
