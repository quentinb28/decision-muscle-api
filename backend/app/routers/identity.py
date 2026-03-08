from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated

from db.session import get_db
from app.auth import get_current_user
from app.services.decision_logger import start_decision_session, log_event
from app.ai.extract_top_values import extract_top_values

from schemas.identity_anchor import IdentityAnchorCreate

from models.user import User
from models.identity_anchor import IdentityAnchor
from models.value_compass import ValueCompass
from models.value_score import ValueScore


router = APIRouter()

DBSession = Annotated[Session, Depends(get_db)]


@router.post("/identity_anchor")
def create_identity_anchor(
    payload: IdentityAnchorCreate,
    db: DBSession,
    current_user: User = Depends(get_current_user)
):

    session = start_decision_session(
        db,
        current_user.id,
        "identity_anchor_created"
    )

    # create identity anchor
    db_identity_anchor = IdentityAnchor(
        user_id=current_user.id,
        description=payload.description
    )

    db.add(db_identity_anchor)
    db.flush()  # get ID without committing

    # create value compass
    db_value_compass = ValueCompass(
        identity_anchor_id=db_identity_anchor.id,
        user_id=current_user.id
    )

    db.add(db_value_compass)
    db.flush()

    # extract top values from AI
    top_values = extract_top_values([payload.description])

    value_pairs = []

    for value, score in top_values:

        db_value_score = ValueScore(
            value_compass_id=db_value_compass.id,
            values=value,
            scores=score
        )

        db.add(db_value_score)

        value_pairs.append({
            "value": value,
            "score": score
        })

    # single commit
    db.commit()

    # log event
    log_event(
        db,
        session.id,
        "identity_anchor_created",
        payload={
            "description": payload.description,
            "values": value_pairs
        }
    )

    return {
        "message": "Identity anchor created",
        "values": value_pairs
    }
