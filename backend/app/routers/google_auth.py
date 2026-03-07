from fastapi import APIRouter, Request, Depends
from db.session import get_db
from sqlalchemy.orm import Session
from app.services.google_auth import create_google_flow
from app.auth import get_current_user
from models.user import User

router = APIRouter()


@router.get("/auth/google")
def connect_google(
    # current_user: User = Depends(get_current_user)
):

    flow = create_google_flow()

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true"
    )

    return {"url": authorization_url}

@router.get("/auth/google/callback")
def google_callback(
    request: Request, 
    db: Session = Depends(get_db)
):

    flow = create_google_flow()

    flow.fetch_token(authorization_response=str(request.url))

    credentials = flow.credentials

    access_token = credentials.token
    refresh_token = credentials.refresh_token

    # identify user (you may store temporary state)
    user_id = request.query_params.get("state")

    user = db.query(User).filter(User.id == user_id).first()

    user.google_access_token = access_token
    user.google_refresh_token = refresh_token

    db.commit()

    return {"status": "Google Calendar connected"}
