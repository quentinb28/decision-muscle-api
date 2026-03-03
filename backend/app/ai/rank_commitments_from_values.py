from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

client = OpenAI()

def rank_commitments_from_values(decision_context, values):

    prompt = f"""
    You are a decision-support assistant focused on value-aligned action.

    Given the user's current decision context:

    "{decision_context}"

    And their stated values with importance scores:

    {values}

    Your task is to:

    1. Identify plausible next-step commitments that are explicitly or implicitly suggested by the user's decision context.
    - Do NOT invent long-term goals.
    - Only extract short-term commitments that could realistically be completed within 48 hours.

    2. For each identified commitment:

    - Assign an alignment_score (1–10) representing how strongly this commitment aligns with the user's most important values.
    - Identify the primary value driving this score (the value most strongly supported by the commitment).
    - Provide a concise one-sentence justification explaining why the commitment aligns with that value.

    1 = weak alignment  
    10 = very strong alignment  

    3. Return exactly the top 3 commitments ranked from highest to lowest alignment_score.

    Return ONLY valid JSON in this format:

    [
    {{
        "commitment": "...",
        "alignment_score": int,
        "main_driver": "...",
        "justification": "..."
    }}
    ]

    Where:
    - Each commitment is realistically completable within 48 hours
    - alignment_score ∈ [1–10]
    - main_value_driver must be one of the user’s provided values
    - justification must be concise (max 1 sentence)
    - The list must be ordered from highest to lowest alignment_score
    """

    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=[
            {
                "role": "system",
                "content": "You prioritize short-term commitments based on user-defined values."
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

    # Defensive sort
    priorities = sorted(
        parsed,
        key=lambda x: x["alignment_score"],
        reverse=True
    )[:3]

    return priorities
