def compute_capacity_score(
        sleep_quality: int, 
        stress_level: int, 
        energy_level: int, 
        emotional_state: int, 
        social_demand: int
) -> int:
    
    positive = (
        sleep_quality +
        energy_level +
        emotional_state
    )

    negative = (
        6 - stress_level +
        6 - social_demand
    )

    total_score = positive + negative  # max = 25, min = 5

    capacity_score = int(((total_score - 5) / 20) * 100)

    return max(1, min(capacity_score, 100))
