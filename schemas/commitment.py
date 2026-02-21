from pydantic import BaseModel
from datetime import datetime

class CommitmentCreate(BaseModel):
    id: int
    decision_id: int
    user_id: str
    next_step: str
    deadline: datetime
    self_generated: bool
    created_at: datetime
