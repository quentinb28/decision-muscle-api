from flask import Blueprint, request, jsonify
from controllers.value_extraction import extract_values
from controllers.pairwise_ranking import generate_pairwise_questions
from controllers.option_generation import generate_options

# Create a Blueprint for identity-related routes
identity_routes = Blueprint('identity', __name__)

# Route for extracting values
@identity_routes.route('/api/extract-values', methods=['POST'])
def extract_values_route():
    data = request.json
    values = extract_values(data['anchor'], os.getenv('OPENAI_API_KEY'))
    return jsonify({"values": values})

# Route for generating pairwise questions
@identity_routes.route('/api/generate-pairwise-questions', methods=['POST'])
def generate_pairwise_questions_route():
    data = request.json
    questions = generate_pairwise_questions(data['values'], os.getenv('OPENAI_API_KEY'))
    return jsonify({"questions": questions})

# Route for generating options
@identity_routes.route('/api/generate-options', methods=['POST'])
def generate_options_route():
    data = request.json
    options = generate_options(data['decision'], data['values'], os.getenv('OPENAI_API_KEY'))
    return jsonify({"options": options})
