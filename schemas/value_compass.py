from pydantic import BaseModel
from datetime import datetime
from typing import List

class ValueCompassCreate(BaseModel):
    id: int
    identity_anchor_id: int
    created_at: datetime
