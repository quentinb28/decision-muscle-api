from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()
client = OpenAI()

def rank_commitments_from_wisdom(decision_context: str):

    prompt = f"""
    You are a decision-support assistant focused on long-term regret minimization.

    Given the user's current decision context:

    "{decision_context}"

    Your task is to:

    1. Identify plausible next-step commitments explicitly or implicitly suggested by the user's situation.
    - Do NOT invent unrelated goals.
    - Only extract commitments that could realistically be completed within 48 hours.

    2. Evaluate each commitment against the five empirically documented regret categories:

    - Unlived potential
    - Unexpressed identity
    - Unrisked growth
    - Unfelt connection
    - Unchallenged comfort

    3. For each commitment:

    - Assign a regret_score (1–10) representing how likely the user would regret NOT doing this in 5–10 years.
    - Identify the primary regret category driving this score.
    - Provide a concise one-sentence justification explaining the score.

    1 = no meaningful long-term regret  
    10 = high likelihood of long-term regret  

    4. Return exactly the top 3 commitments ranked from highest to lowest regret_score.

    Return ONLY valid JSON in this format:

    [
    {{
        "commitment": "...",
        "regret_score": int,
        "main_driver": "...",
        "justification": "..."
    }}
    ]

    Where:
    - Each commitment is realistically completable within 48 hours
    - regret_score ∈ [1–10]
    - main_regret_driver must be one of the five regret categories
    - justification must be concise (max 1 sentence)
    - The list must be ordered from highest to lowest regret_score
    """

    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=[
            {
                "role": "system",
                "content": "You prioritize short-term actions that reduce long-term regret."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    raw_output = response.choices[0].message.content

    # Remove markdown fences
    cleaned = re.sub(r"```json|```", "", raw_output).strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        raise ValueError(f"AI output not valid JSON:\n{cleaned}")

    # Defensive sorting
    priorities = sorted(
        parsed,
        key=lambda x: x["regret_score"],
        reverse=True
    )[:3]

    return priorities
