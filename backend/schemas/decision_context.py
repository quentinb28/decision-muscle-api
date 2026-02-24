from pydantic import BaseModel
from datetime import datetime

class DecisionContextCreate(BaseModel):
    description: str
