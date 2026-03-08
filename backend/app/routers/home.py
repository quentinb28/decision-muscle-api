from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated

from db.session import get_db
from app.auth import get_current_user
from app.services.decision_logger import start_decision_session, log_event

from models.user import User
from models.identity_anchor import IdentityAnchor
from models.decision_context import DecisionContext
from models.commitment import Commitment


router = APIRouter()

DBSession = Annotated[Session, Depends(get_db)]


@router.get("/home")
def get_home_state(
    db: DBSession,
    current_user: User = Depends(get_current_user)
):

    session = start_decision_session(
        db,
        current_user.id,
        "home_load"
    )

    # latest identity anchor
    latest_identity_anchor = (
        db.query(IdentityAnchor)
        .filter(IdentityAnchor.user_id == current_user.id)
        .order_by(IdentityAnchor.created_at.desc())
        .first()
    )

    # latest decision context
    latest_decision_context = (
        db.query(DecisionContext)
        .filter(DecisionContext.user_id == current_user.id)
        .order_by(DecisionContext.created_at.desc())
        .first()
    )

    # active commitments
    active_commitments = (
        db.query(Commitment)
        .filter(
            Commitment.user_id == current_user.id,
            Commitment.status == "active"
        )
        .all()
    )

    remaining_slots = max(0, 3 - len(active_commitments))

    # log snapshot
    log_event(
        db,
        session.id,
        "context_snapshot",
        payload={
            "identity_anchor_exists": latest_identity_anchor is not None,
            "decision_context_exists": latest_decision_context is not None,
            "remaining_slots": remaining_slots,
            "active_commitments": len(active_commitments)
        },
        decision_context_id=latest_decision_context.id if latest_decision_context else None
    )

    return {
        "identity_anchor": {
            "exists": latest_identity_anchor is not None,
            "description": latest_identity_anchor.description if latest_identity_anchor else None
        },
        "decision_context": latest_decision_context.description if latest_decision_context else None,
        "remaining_slots": remaining_slots,
        "active_commitments": [
            {
                "id": c.id,
                "text": c.commitment,
                "due_at": c.due_at
            }
            for c in active_commitments
        ]
    }
