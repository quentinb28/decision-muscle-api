from openai import OpenAI
from sqlalchemy.orm import Session
from models.decision_context import DecisionContext
from models.value_score import ValueScore
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI()

def generate_suggestions(user_id: str, db: Session):

    # 1️⃣ fetch decision context
    dc = db.query(DecisionContext).filter(
         DecisionContext.user_id == user_id
         ).order_by(
        DecisionContext.created_at.desc()
        ).first()

    if not dc:
        return {"error": "Decision context not found"}

    # 2️⃣ fetch top 3 values from linked VC
    top_values = db.query(ValueScore)\
        .filter(ValueScore.value_compass_id == dc.value_compass_id)\
        .order_by(ValueScore.scores.desc())\
        .limit(3)\
        .all()

    values_str = "\n".join([
        f"{v.values}: {round(v.scores, 2)}"
        for v in top_values
        ])

    # 3️⃣ build prompt
    prompt = f"""
    User decision context:
    {dc.description}

    Top personal values:
    {values_str}

    Create exactly 3 specific 48-hour commitments aligned with these values.

    Rules:
    - Must be actionable within 48 hours
    - Must start with "I will"
    - Must be concrete (observable)
    - No vague advice
    - No long-term goals

    Return as a numbered list.
    """

    # 4️⃣ call LLM
    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=[
            {"role": "system", "content": "You generate aligned short-term commitments."},
            {"role": "user", "content": prompt}
            ]
            )

    output = response.choices[0].message.content

    # 5️⃣ parse list
    suggestions = [
        line.split(".",1)[1].strip()
        for line in output.split("\n")
        if line.strip().startswith(("1","2","3"))
        ]

    return suggestions[:3]
