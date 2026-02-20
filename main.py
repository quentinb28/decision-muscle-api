from fastapi import FastAPI
from db.base import Base
from db.session import engine

from models.decision import Decision

from schemas.commitment import CommitmentCreate
from models.commitment import Commitment

from schemas.followthrough import FollowThroughCreate
from models.proof import FollowThrough

app = FastAPI()
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "Decision Integrity Engine Running"}

decisions = []

@app.post("/decisions")
def create_decision(decision: Decision):
    decisions.append(decision)
    return {"message": "Decision logged"}

@app.post("/commitments")
def create_commitment(commitment: CommitmentCreate):
    db = SessionLocal()

    db_commitment = Commitment(
        decision_id=commitment.decision_id,
        next_step=commitment.next_step
    )

    db.add(db_commitment)
    db.commit()
    db.refresh(db_commitment)

    db.close()

    return {"message": "Commitment created"}

@app.post("/follow-through")
def follow_through(report: FollowThroughCreate):
    db = SessionLocal()

    # Save follow-up proof
    db_followup = FollowThrough(
        commitment_id=report.commitment_id,
        completed=report.completed,
        alignment_rating=report.alignment_rating
    )
    db.add(db_followup)

    # Update commitment completion status
    commitment = db.query(Commitment).filter(
        Commitment.id == report.commitment_id
    ).first()

    if commitment:
        commitment.completed = report.completed

    db.commit()
    db.close()

    return {"message": "Follow-through recorded"}

from app.metrics.integrity_score import calculate_integrity_score

@app.get("/metrics/integrity-score")
def get_integrity_score():
    score = calculate_integrity_score(followups)
    return {"integrity_score": score}

from app.metrics.follow_through_rate import calculate_follow_through_rate

@app.get("/metrics/follow-through-rate")
def get_follow_through_rate():
    db = SessionLocal()

    commitments = db.query(Commitment).all()

    score = calculate_follow_through_rate(commitments)

    db.close()

    return {"follow_through_rate": score}

# $ python -m uvicorn main:app --reload --port 8001
# lsof -i :8001
# kill -9 12569