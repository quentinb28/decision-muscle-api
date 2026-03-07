from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated

from db.session import get_db
from app.auth import get_current_user
from app.services.decision_logger import start_decision_session, log_event
from app.ai.rank_commitments_from_values import rank_commitments_from_values
from app.ai.rank_commitments_from_wisdom import rank_commitments_from_wisdom

from schemas.commitment import CommitmentCreate

from models.user import User
from models.value_compass import ValueCompass
from models.value_score import ValueScore

from models.decision_context import DecisionContext

router = APIRouter()

DBSession = Annotated[Session, Depends(get_db)]


@router.post("/prioritization_filter")
def create_prioritization_filter(
    db: DBSession, 
    current_user: User = Depends(get_current_user)
):

    session = start_decision_session(db, current_user.id, "prioritization_filter")

    latest_decision_context = (
        db.query(DecisionContext)
        .filter(DecisionContext.user_id == current_user.id)
        .order_by(DecisionContext.created_at.desc())
        .first()
    )

    if not latest_decision_context:
        return {"error": "Decision context not found"}

    latest_value_compass = (
        db.query(ValueCompass)
        .filter(ValueCompass.user_id == current_user.id)
        .order_by(ValueCompass.created_at.desc())
        .first()
    )

    if latest_value_compass:

        top_values = (
            db.query(ValueScore)
            .filter(ValueScore.value_compass_id == latest_value_compass.id)
            .order_by(ValueScore.scores.desc())
            .all()
        )

        values_str = "\n".join(
            [f"{v.values}: {round(v.scores, 2)}" for v in top_values]
        )

        priorities = rank_commitments_from_values(
            latest_decision_context.description,
            values_str
        )

        mode = "values"

    else:

        priorities = rank_commitments_from_wisdom(
            latest_decision_context.description
        )

        mode = "wisdom"

    log_event(
        db,
        session.id,
        "prioritization_filter_applied",
        payload={
            "mode": mode,
            "priorities": priorities
        },
        decision_context_id=latest_decision_context.id
    )

    response = {
        f"priority{i+1}": value
        for i, value in enumerate(priorities)
    }

    response["mode"] = mode

    return response
