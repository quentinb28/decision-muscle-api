from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_commitment_appraisal(candidate_commitment: str) -> int:


    prompt = f"""
    You are a decision-support assistant.

    Given the following action:

    "{candidate_commitment}"

    Rate the expected:
    - cognitive demand (1–10)
    - emotional demand (1–10)
    - time pressure (1–10)

    Guidelines:
    1 = very low demand
    10 = extremely demanding

    Return ONLY valid JSON in this format:
    {{
    "cognitive_demand": int,
    "emotional_demand": int,
    "time_pressure": int
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You evaluate task demands for feasibility estimation."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    result = json.loads(response.choices[0].message.content)

    avg_score = round(
        (
        result["cognitive_demand"] + 
        result["emotional_demand"] +
        result["time_pressure"]
    ) / 3, 
    2)

    return min(max(avg_score, 1), 10)
