from pydantic import BaseModel
from datetime import datetime

class ExecutionCreate(BaseModel):
    id: int
    commitment_id: int
    completed: bool
    alignment_rating: float
    executed_at: datetime
