from pydantic import BaseModel
from typing import List, Optional

class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    dates: List[str]
    place: Optional[str] = None
    outstanding: bool = False
    image_url: Optional[str] = None

class EventCreate(EventBase):
    pass

class Event(EventBase):
    id: int

    class Config:
        from_attributes = True  # Pydantic v2
