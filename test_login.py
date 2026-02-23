from dotenv import load_dotenv
import os
from supabase import create_client

load_dotenv()

SUPABASE_URL = "https://ubaicyenptbgyayhnwpq.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_IS9wyZx3UGH_0D010hYtiQ_NbcvXogA"

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def login():

    response = supabase.auth.sign_in_with_password({
        "email": "test@email.com",
        "password": "password123"
    })

    print("\nACCESS TOKEN:\n")
    print(response.session.access_token)


login()
