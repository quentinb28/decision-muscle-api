from pydantic import BaseModel

class FollowThrough(BaseModel):
    commitment_id: int
    completed: bool
    alignment_rating: int