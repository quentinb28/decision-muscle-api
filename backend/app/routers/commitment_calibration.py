from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Annotated

from db.session import get_db
from app.auth import get_current_user
from app.services.decision_logger import start_decision_session, log_event

from app.ai.generate_commitment_appraisal import generate_commitment_appraisal
from app.ai.generate_scaled_commitments import generate_scaled_commitments

from schemas.commitment_calibration import CommitmentCalibrationCreate

from models.user import User


router = APIRouter()

DBSession = Annotated[Session, Depends(get_db)]


@router.post("/commitment_calibration")
def create_commitment_calibration(
    payload: CommitmentCalibrationCreate,
    db: DBSession,
    current_user: User = Depends(get_current_user)
):

    session = start_decision_session(
        db,
        current_user.id,
        "commitment_evaluation"
    )

    baseline_capacity = payload.baseline_capacity
    candidate_commitment = payload.candidate_commitment

    # AI appraisal of commitment demand
    commitment_appraisal = generate_commitment_appraisal(
        candidate_commitment
    )

    # compute adjusted capacity
    adjusted_capacity = int(
        round(
            max(1, baseline_capacity * (1 - commitment_appraisal / 10))
        )
    )

    # recommendation logic
    recommendation = None
    alternatives = []

    if adjusted_capacity >= 40:

        recommendation = "keep"

    elif adjusted_capacity >= 20:

        recommendation = "kneel"

        alternatives = generate_scaled_commitments(
            candidate_commitment
        )

    else:

        recommendation = "kill"

        alternatives = generate_scaled_commitments(
            candidate_commitment
        )

    log_event(
        db,
        session.id,
        "commitment_evaluated",
        payload={
            "candidate_commitment": candidate_commitment,
            "baseline_capacity": baseline_capacity,
            "commitment_appraisal": commitment_appraisal,
            "adjusted_capacity": adjusted_capacity,
            "recommendation": recommendation,
            "alternatives": alternatives
        }
    )

    return {
        "baseline_capacity": baseline_capacity,
        "commitment_appraisal": commitment_appraisal,
        "adjusted_capacity": adjusted_capacity,
        "recommendation": recommendation,
        "alternatives": alternatives
    }
