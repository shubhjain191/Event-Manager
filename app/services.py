import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from .models import Event

class EventService:
    def __init__(self, data_file: str):
        self.data_file = data_file
        self._ensure_data_directory()
        self.events: List[Event] = self._load_events()
    
    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
    
    def _load_events(self) -> List[Event]:
        """Load events from JSON file"""
        if not os.path.exists(self.data_file):
            return []
        
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                return [Event.from_dict(event_data) for event_data in data]
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_events(self):
        """Save events to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump([event.to_dict() for event in self.events], f, indent=2)
    
    def create_event(self, title: str, description: str, start_time: str, 
                    end_time: str, recurrence: str = None) -> Event:
        """Create a new event"""
        event = Event(title, description, start_time, end_time, recurrence=recurrence)
        self.events.append(event)
        self._save_events()
        return event
    
    def get_all_events(self, sort_by_time: bool = True) -> List[Event]:
        """Get all events, optionally sorted by start time"""
        if sort_by_time:
            return sorted(self.events, key=lambda e: e.start_time)
        return self.events.copy()
    
    def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """Get event by ID"""
        return next((event for event in self.events if event.id == event_id), None)
    
    def update_event(self, event_id: str, **kwargs) -> Optional[Event]:
        """Update an existing event"""
        event = self.get_event_by_id(event_id)
        if not event:
            return None
        
        # Update fields if provided
        if 'title' in kwargs:
            event.title = kwargs['title']
        if 'description' in kwargs:
            event.description = kwargs['description']
        if 'start_time' in kwargs:
            event.start_time = event._parse_datetime(kwargs['start_time'])
        if 'end_time' in kwargs:
            event.end_time = event._parse_datetime(kwargs['end_time'])
        if 'recurrence' in kwargs:
            event.recurrence = kwargs['recurrence']
        
        # Validate times after update
        if event.start_time >= event.end_time:
            raise ValueError("Start time must be before end time")
        
        self._save_events()
        return event
    
    def delete_event(self, event_id: str) -> bool:
        """Delete an event"""
        event = self.get_event_by_id(event_id)
        if event:
            self.events.remove(event)
            self._save_events()
            return True
        return False
    
    def search_events(self, query: str = None, start_date: str = None, 
                     end_date: str = None, recurrence: str = None) -> List[Event]:
        """
        Advanced search events with multiple filters
        
        Args:
            query: Search in title and description
            start_date: Filter events starting from this date (ISO format)
            end_date: Filter events ending before this date (ISO format)
            recurrence: Filter by recurrence type ('daily', 'weekly', 'monthly', None)
        """
        filtered_events = self.events.copy()
        
        if query:
            query_lower = query.lower()
            filtered_events = [
                event for event in filtered_events
                if query_lower in event.title.lower() or query_lower in event.description.lower()
            ]
        
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                filtered_events = [
                    event for event in filtered_events
                    if event.start_time >= start_datetime
                ]
            except ValueError:
                pass  
        
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                filtered_events = [
                    event for event in filtered_events
                    if event.end_time <= end_datetime
                ]
            except ValueError:
                pass 
        
        if recurrence is not None:
            filtered_events = [
                event for event in filtered_events
                if event.recurrence == recurrence
            ]
        
        return sorted(filtered_events, key=lambda e: e.start_time)
    
    def get_upcoming_reminders(self, minutes: int = 60) -> List[Event]:
        """Get events that are due within specified minutes"""
        return [event for event in self.events if event.is_due_soon(minutes)]
    
    def get_events_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Event]:
        """Get events within a specific date range"""
        return [
            event for event in self.events
            if start_date <= event.start_time <= end_date
        ]
    
    def get_today_events(self) -> List[Event]:
        """Get all events scheduled for today"""
        today = datetime.now().date()
        return [
            event for event in self.events
            if event.start_time.date() == today
        ]
    
    def get_week_events(self) -> List[Event]:
        """Get all events scheduled for the current week"""
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        return self.get_events_by_date_range(
            datetime.combine(week_start, datetime.min.time()),
            datetime.combine(week_end, datetime.max.time())
        )