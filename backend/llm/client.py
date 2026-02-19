import os 
from openai import OpenAI
# from src.config import get_api_key

def get_client():
    return OpenAI(api_key=os.getenv('OPENAI_API_KEY'))