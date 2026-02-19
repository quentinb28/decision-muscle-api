def generate_options(decision, values, openai_api_key):
    openai.api_key = openai_api_key
    prompt = f"Given the decision '{decision}' and the values {', '.join(values)}, generate three options: Comfort Option, Avoidance Option, and Aligned Option."
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    options = response['choices'][0]['message']['content'].strip().split('\n')
    return {
        "comfort": options[0],
        "avoidance": options[1],
        "aligned": options[2]
    }

