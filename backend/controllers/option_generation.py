import os
import ast
import json
from llm.client import get_client

client = get_client()
MODEL = os.getenv("MODEL")

def generate_options(decision, values):

    prompt = (
        f"""Given the decision '{decision}' 
        and the values {', '.join(values)}, 
        generate three options that reflect different approaches: 
        1. Comfort Option: a choice that maintains the current state despite its drawbacks.
        2. Avoidance Option: a choice that avoids facing the decision, potentially leading to negative consequences.
        3. Aligned Option: take into account values and significance weight, addressing potential value tensions.
        Please ensure that the Aligned Option considers how to balance these values and the tensions that may arise from pursuing this path.Then provide the options in the format: Comfort: Option, Avoidance: Option, Aligned: Option."""
    )

    try:    
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        # Extracting the response content
        options = response.choices[0].message.content.strip()

        return {"options": json.loads(options)["options"]}

    except Exception as e:
        return {"options": {"error": str(e)}}
