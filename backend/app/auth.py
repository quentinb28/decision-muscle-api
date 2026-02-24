from jose import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests

security = HTTPBearer()

JWKS_URL = "https://ubaicyenptbgyayhnwpq.supabase.co/auth/v1/.well-known/jwks.json"


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        # fetch Supabase public keys
        jwks = requests.get(JWKS_URL).json()

        # get token header
        unverified_header = jwt.get_unverified_header(token)

        # find correct key
        key = next(
            k for k in jwks["keys"]
            if k["kid"] == unverified_header["kid"]
        )

        # jose supports EC directly
        payload = jwt.decode(
            token,
            key,
            algorithms=["ES256"],
            audience="authenticated"
        )

        return payload["sub"]

    except Exception as e:
        print("JWT ERROR:", e)
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )
    