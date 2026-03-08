from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated

from db.session import get_db
from app.auth import get_current_user
from app.services.decision_logger import start_decision_session, log_event

from app.ai.compute_capacity_score import compute_capacity_score

from schemas.capacity_snapshot import CapacitySnapshotCreate

from models.user import User


router = APIRouter()

DBSession = Annotated[Session, Depends(get_db)]


@router.post("/capacity_snapshot")
def create_capacity_snapshot(
    payload: CapacitySnapshotCreate,
    db: DBSession,
    current_user: User = Depends(get_current_user)
):

    # start decision session
    session = start_decision_session(
        db,
        current_user.id,
        "capacity_check"
    )

    # compute baseline capacity
    capacity_score = compute_capacity_score(
        sleep_quality=payload.sleep_quality,
        stress_level=payload.stress_level,
        energy_level=payload.energy_level,
        emotional_state=payload.emotional_state,
        social_demand=payload.social_demand
    )

    # log event
    log_event(
        db,
        session.id,
        "capacity_calculated",
        payload={
            "baseline_capacity": capacity_score,
            "sleep_quality": payload.sleep_quality,
            "stress_level": payload.stress_level,
            "energy_level": payload.energy_level,
            "emotional_state": payload.emotional_state,
            "social_demand": payload.social_demand
        }
    )

    # response
    return {
        "baseline_capacity": capacity_score
    }
