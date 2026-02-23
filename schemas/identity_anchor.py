from pydantic import BaseModel
from datetime import datetime

class IdentityAnchorCreate(BaseModel):
    description: str