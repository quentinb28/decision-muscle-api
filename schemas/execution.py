from pydantic import BaseModel
from datetime import datetime

class ExecutionCreate(BaseModel):
    id: int
    commitment_id: int
    outcome: str
    executed_at: datetime
