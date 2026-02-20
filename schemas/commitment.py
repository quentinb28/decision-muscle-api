from pydantic import BaseModel

class CommitmentCreate(BaseModel):
    decision_id: int
    next_step: str
