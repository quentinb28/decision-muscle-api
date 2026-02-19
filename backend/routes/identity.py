from controllers.value_extraction import get_values

@identity_routes.route('/api/extract-values', methods=['POST'])
def extract_values_route():
    return get_values(request)

from controllers.pairwise_ranking import generate_pairwise_questions

@identity_routes.route('/api/generate-pairwise-questions', methods=['POST'])
def generate_pairwise_questions_route():
    data = request.json
    questions = generate_pairwise_questions(data['values'], os.getenv('OPENAI_API_KEY'))
    return jsonify({"questions": questions})

@identity_routes.route('/api/generate-options', methods=['POST'])
def generate_options_route():    
    data = request.json    
    options = generate_options(data['decision'], data['values'], os.getenv('OPENAI_API_KEY'))    
    return jsonify({"options": options})

@identity_routes.route('/api/submit-options', methods=['POST'])
def submit_options():
    data = request.json
    # Save options to database or process further
    return jsonify({"message": "Options submitted successfully"}), 201

