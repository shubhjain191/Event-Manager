from datetime import datetime
from typing import Dict, Any, Optional
import uuid

class Event:
    def __init__(self, title: str, description: str, start_time: str, 
                 end_time: str, event_id: str = None, recurrence: str = None):
        self.id = event_id or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.start_time = self._parse_datetime(start_time)
        self.end_time = self._parse_datetime(end_time)
        self.recurrence = recurrence
        self.created_at = datetime.now()
        
        if self.start_time >= self.end_time:
            raise ValueError("Start time must be before end time")
    
    def _parse_datetime(self, dt_string: str) -> datetime:
        """Parse datetime string in ISO format"""
        try:
            return datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError(f"Invalid datetime format: {dt_string}. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'recurrence': self.recurrence,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create event from dictionary"""
        event = cls(
            title=data['title'],
            description=data['description'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            event_id=data['id'],
            recurrence=data.get('recurrence')
        )
        if 'created_at' in data:
            event.created_at = datetime.fromisoformat(data['created_at'])
        return event
    
    def is_due_soon(self, minutes: int = 60) -> bool:
        """Check if event is due within specified minutes"""
        now = datetime.now()
        time_diff = (self.start_time - now).total_seconds() / 60
        return 0 <= time_diff <= minutes