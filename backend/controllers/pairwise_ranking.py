def generate_pairwise_questions(values, openai_api_key):
    openai.api_key = openai_api_key
    prompt = f"Generate pairwise ranking questions for the following values: {', '.join(values)}. Each question should compare two values."
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    questions = response['choices'][0]['message']['content'].strip().split('\n')
    return questions

