from datetime import datetime

from fastapi import FastAPI, BackgroundTasks, Depends
from db.base import Base
from db.session import engine, SessionLocal

from models.identity_anchor import IdentityAnchor
from models.value_compass import ValueCompass
from models.value_score import ValueScore
from models.decision import Decision
from models.commitment import Commitment
from models.execution import Execution

from schemas.identity_anchor import IdentityAnchorCreate
# from schemas.value_compass import ValueCompassCreate
# from schemas.value_score import ValueScoreCreate
from schemas.decision import DecisionCreate
from schemas.commitment import CommitmentCreate
from schemas.execution import ExecutionCreate

from app.ai.extract_values import extract_top_values

from app.metrics.follow_through_rate import calculate_follow_through_rate
# from app.metrics.self_leadership_rate import calculate_self_leadership_rate
# from app.metrics.integrity_score import calculate_integrity_score
# from app.metrics.alignment_score import calculate_alignment_score

app = FastAPI() # https://localhost/docs (ex. http://127.0.0.1:8001/docs)
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "Decision Integrity Engine Running"}

@app.post("/identity_anchors")
def create_identity_anchor(identity_anchor: IdentityAnchorCreate):

    db = SessionLocal()

    try:
        # --- create identity anchor ---
        db_identity_anchor = IdentityAnchor(
            user_id=identity_anchor.user_id,
            description=identity_anchor.description,
            created_at=identity_anchor.created_at
            )

        db.add(db_identity_anchor)
        db.commit()
        db.refresh(db_identity_anchor)

        # --- create value compass ---
        db_value_compass = ValueCompass(
            identity_anchor_id=db_identity_anchor.id,
            created_at=db_identity_anchor.created_at
            )
        
        db.add(db_value_compass)
        db.commit()
        db.refresh(db_value_compass)

        # --- extract top values from identity anchor ---
        top_values = extract_top_values([db_identity_anchor.description])

        # --- create value compass ---
        for (value, score) in top_values:
            db_value_score = ValueScore(
                value_compass_id=db_value_compass.id,
                values=value,
                scores=score
                )

            db.add(db_value_score)
            db.commit()
            db.refresh(db_value_score)

        return {"message": "Identity Anchor + Value Compass registered"}

    finally:
        db.close()

@app.get("/identity_anchors/{user_id}")
def get_active_identity_anchor(user_id: str):

    db = SessionLocal()

    identity_anchor = db.query(IdentityAnchor).filter(
        IdentityAnchor.user_id == user_id
    ).order_by(
        IdentityAnchor.created_at.desc()
    ).first()

    db.close()

    if not identity_anchor:
        return {"message": "No identity anchor found"}

    return identity_anchor

# @app.get("/value-compasses/{user_id}")
# def get_latest_value_compass(user_id: int, db: DBSession):
    
#     return (
#         db.query(ValueCompass)
#         .filter(ValueCompass.user_id == user_id)
#         .order_by(ValueCompass.created_at.desc())
#         .first()
#     )

@app.post("/decisions")
def create_decision(decision: DecisionCreate):

    db = SessionLocal()

    db_decision = Decision(
        user_id=decision.user_id,
        decision_id=decision.decision_id,
        description=decision.description
    )

    db.add(db_decision)
    db.commit()
    db.refresh(db_decision)

    db.close()

    return {"message": "Decision logged"}

@app.post("/commitments")
def create_commitment(commitment: CommitmentCreate):
    db = SessionLocal()

    db_commitment = Commitment(
        commitment_id=commitment.commitment_id,
        decision_id=commitment.decision_id,
        user_id=commitment.user_id,
        next_step=commitment.next_step,
        deadline=commitment.deadline,
        self_generated=commitment.self_generated,
        created_at=commitment.created_at
    )

    db.add(db_commitment)
    db.commit()
    db.refresh(db_commitment)

    db.close()

    return {"message": "Commitment created"}

@app.post("/executions")
def create_execution(execution: ExecutionCreate):
    db = SessionLocal()

    # Save follow-up proof
    db_execution = Execution(
        execution_id=execution.execution_id,
        commitment_id=execution.commitment_id,
        completed=execution.completed,
        alignment_rating=execution.alignment_rating,
        executed_at=execution.executed_at
    )
    db.add(db_execution)
    db.commit()
    db.refresh(db_execution)

    db.close()

    return {"message": "Execution recorded"}

@app.get("/metrics/follow-through-rate/{user_id}")
def get_follow_through_rate(user_id: str):

    db = SessionLocal()

    # 1. Get all commitments for user
    commitments = db.query(Commitment).filter(
        Commitment.user_id == user_id
    ).all()

    if len(commitments) == 0:
        db.close()
        return {"Follow Through Rate (FTR)": 0}
    
    completed_count = 0

    # 2. For each commitment, get latest execution
    for commitment in commitments:

        latest_execution = db.query(Execution).filter(
            Execution.commitment_id == commitment.commitment_id
        ).order_by(
            Execution.executed_at.desc()
        ).first()

        # 3. Check if latest execution completed
        if latest_execution and latest_execution.completed:
            completed_count += 1

    # 4. Compute score
    score = completed_count / len(commitments)

    db.close()

    return {"Follow Through Rate (FTR)": score}

# $ python -m uvicorn main:app --reload --port 8001
# lsof -i :8001
# kill -9 12569
# sqlite3 test.db
