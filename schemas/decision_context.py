from pydantic import BaseModel
from datetime import datetime

class DecisionContextCreate(BaseModel):
    id: int
    user_id: str
    description: str
    value_compass_id: int
    created_at: datetime
