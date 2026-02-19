import os
import openai
from llm.client import get_client

client = get_client()
MODEL = os.getenv("MODEL")

def extract_values(anchor_text):
    prompt = (
        f"""Given the following identity anchor: '{anchor_text}', 
        identify the most relevant values and assign automatic significance scores 
        based on their importance to the user. The values should be assigned the 
        following scores: .10, .15, .20, .25, and .30. 
        Please provide the values along with their corresponding scores in the 
        format: value1: score1, value2: score2, ... 
        Ensure that the total number of values does not exceed five, and the scores 
        should reflect their relative significance in accordance with the assigned values."""
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    content = response.choices[0].message.content.strip()
    
    # Parse the content into a dictionary
    values_scores = {}
    for item in content.split(', '):
        value, score = item.split(': ')
        values_scores[value.strip()] = float(score.strip())
    
    return values_scores

def get_values(request):
    data = request.json
    values = extract_values(data['anchor'], os.getenv('OPENAI_API_KEY'))  # Ensure the API key is set in your environment
    return jsonify({"values": values})

