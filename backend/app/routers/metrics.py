from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated

from db.session import get_db
from app.auth import get_current_user

from models.user import User
from models.commitment import Commitment

router = APIRouter()

DBSession = Annotated[Session, Depends(get_db)]


@router.get("/metrics/follow-through-rate")
def get_follow_through_rate(
    db: DBSession, 
    current_user: User = Depends(get_current_user)
):

    # 1. Get all commitments for user
    commitments = db.query(Commitment).filter(
        Commitment.user_id == current_user.id).filter(
        Commitment.status != "active").all(
    )

    if len(commitments) == 0:
        db.close()
        return {"Follow Through Rate (FTR)": 0}
    
    # 2. Count all completed commitments
    completed_count = sum([1 for commitment in commitments if commitment.status == "fully_completed"])

    # 3. Compute score
    score = completed_count / len(commitments)

    db.close()

    return {"Follow Through Rate (FTR)": score}

# @app.get("/metrics/self-leadership-rate")
# def get_self_leadership_rate(
#     db: DBSession, 
#     user_id: str = Depends(get_current_user)
# ):

#     # 1. Get all commitments for user
#     commitments = db.query(Commitment).filter(
#         Commitment.user_id == user_id).all(
#     )

#     if len(commitments) == 0:
#         db.close()
#         return {"Self Leadership Rate (SLR)": 0}
    
#     # 2. Count all self endorsed commitments
#     self_endorsed_count = sum([1 for commitment in commitments if commitment.source == "self_endorsed"])

#     # 3. Compute score
#     score = self_endorsed_count / len(commitments)

#     db.close()

#     return {"Self Leadership Rate (SLR)": score}
