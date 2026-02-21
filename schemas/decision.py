from pydantic import BaseModel
from datetime import datetime

class DecisionCreate(BaseModel):
    decision_id: int
    user_id: str
    description: str
