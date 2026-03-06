from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated

from db.session import get_db
from app.auth import get_current_user
from app.services.decision_logger import start_decision_session, log_event
from app.ai.compute_capacity_score import compute_capacity_score

from schemas.capacity_snapshot import CapacitySnapshotCreate

router = APIRouter()

DBSession = Annotated[Session, Depends(get_db)]


@app.post("/capacity_snapshot")
def create_capacity_snapshot(
    payload: CapacitySnapshotCreate,
    db: DBSession,
    user_id: str = Depends(get_current_user)
):

    session = start_decision_session(db, user_id, "capacity_check")

    capacity_score = compute_capacity_score(payload)

    log_event(
        db,
        session.id,
        "capacity_calculated",
        payload={"baseline_capacity": capacity_score}
    )

    return {
        "baseline_capacity": capacity_score
    }
