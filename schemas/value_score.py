from pydantic import BaseModel
from datetime import datetime
from typing import List

class ValueScoreCreate(BaseModel):
    id: int
    value_compass_id: int
    values: str
    scores: float
    