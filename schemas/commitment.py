from pydantic import BaseModel
from datetime import datetime

class CommitmentCreate(BaseModel):
    commitment: str
    source: str
