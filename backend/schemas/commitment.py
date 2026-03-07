from pydantic import BaseModel
from datetime import datetime

class CommitmentCreate(BaseModel):
    commitment: str
    source: str
    start_time: str
    end_time: str
