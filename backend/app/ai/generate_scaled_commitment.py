from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_scaled_commitments(candidate_commitment: str):

    prompt = f"""
    You are a commitment calibration assistant.

    The following commitment is too demanding relative to current capacity:

    "{candidate_commitment}"

    Generate exactly 3 alternative commitments that:

    - Preserve the same direction or intention
    - Are significantly easier to complete
    - Could realistically be completed within 24–48 hours
    - Reduce cognitive, emotional, or time demand

    Return ONLY valid JSON in this format:

    [
    {{"commitment": "..."}},
    {{"commitment": "..."}},
    {{"commitment": "..."}}
    ]
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You downscale commitments while preserving intent."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    raw = response.choices[0].message.content
    parsed = json.loads(raw)

    return parsed
