from pydantic import BaseModel
from datetime import datetime

class ExecutionCreate(BaseModel):
    commitment_id: int
    outcome: str
    comment: str
