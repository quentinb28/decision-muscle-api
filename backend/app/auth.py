import requests
from jose import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db.session import get_db
from sqlalchemy.orm import Session
from models.user import User

security = HTTPBearer()

JWKS_URL = "https://ubaicyenptbgyayhnwpq.supabase.co/auth/v1/.well-known/jwks.json"


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        jwks = requests.get(JWKS_URL).json()

        unverified_header = jwt.get_unverified_header(token)

        key = next(
            k for k in jwks["keys"]
            if k["kid"] == unverified_header["kid"]
        )

        payload = jwt.decode(
            token,
            key,
            algorithms=["ES256"],
            audience="authenticated"
        )
    
        user_id = payload["sub"]

        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            user = User(
                id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            db.add(user)
            db.commit()
            db.refresh(user)

        return user

    except Exception as e:
        print("JWT ERROR:", e)
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )
    
from datetime import datetime, timedelta

SECRET_KEY = "your-secret"
ALGORITHM = "HS256"

def create_access_token(user_id: str):
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)