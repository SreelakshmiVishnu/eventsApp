from sqlalchemy.orm import Session
from models import Event
from schemas import EventCreate
import json

def get_events(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Event).order_by(Event.dates).offset(skip).limit(limit).all()

def get_featured_events(db: Session):
    return db.query(Event).filter(Event.outstanding == True).all()

def get_event(db: Session, event_id: int):
    return db.query(Event).filter(Event.id == event_id).first()

def create_event(db: Session, event: EventCreate):
    db_event = Event(
        name=event.name,
        description=event.description,
        dates=json.dumps(event.dates),  # store as JSON string
        place=event.place,
        outstanding=event.outstanding,
        image_url=event.image_url
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event
