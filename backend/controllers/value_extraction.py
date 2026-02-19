import os
import openai

def extract_values(anchor_text, openai_api_key):
    openai.api_key = openai_api_key
    prompt = (
        f"""Given the following identity anchor: '{anchor_text}', 
        which 5 values from the list 
        (Security, Belonging, Autonomy, Achievement, Status, 
        Integrity, Growth, Contribution, Pleasure, Meaning) 
        are most relevant?"""
    )
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    values = response['choices'][0]['message']['content'].strip().split(', ')
    return values

def get_values(request):
    data = request.json
    values = extract_values(data['anchor'], os.getenv('OPENAI_API_KEY'))  # Ensure the API key is set in your environment
    return jsonify({"values": values})

