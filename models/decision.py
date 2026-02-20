from pydantic import BaseModel

class Decision(BaseModel):
    user_id: str
    description: str
