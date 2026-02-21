from pydantic import BaseModel
from datetime import datetime

class IdentityAnchorCreate(BaseModel):
    id: int
    user_id: str
    description: str
    created_at: datetime
