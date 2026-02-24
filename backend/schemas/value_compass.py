from pydantic import BaseModel
from datetime import datetime
from typing import List

class ValueCompassCreate(BaseModel):
    identity_anchor_id: int
    user_id: str