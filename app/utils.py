from datetime import datetime, timedelta
from typing import List
from .models import Event

def generate_recurring_events(base_event: Event, end_date: datetime) -> List[Event]:
    """Generate recurring events based on base event"""
    if not base_event.recurrence:
        return [base_event]
    
    events = [base_event]
    current_start = base_event.start_time
    current_end = base_event.end_time
    
    while current_start < end_date:
        if base_event.recurrence == 'daily':
            current_start += timedelta(days=1)
            current_end += timedelta(days=1)
        elif base_event.recurrence == 'weekly':
            current_start += timedelta(weeks=1)
            current_end += timedelta(weeks=1)
        elif base_event.recurrence == 'monthly':
            # Simple monthly increment (doesn't handle edge cases perfectly)
            if current_start.month == 12:
                current_start = current_start.replace(year=current_start.year + 1, month=1)
                current_end = current_end.replace(year=current_end.year + 1, month=1)
            else:
                current_start = current_start.replace(month=current_start.month + 1)
                current_end = current_end.replace(month=current_end.month + 1)
        
        if current_start < end_date:
            recurring_event = Event(
                title=f"{base_event.title} (Recurring)",
                description=base_event.description,
                start_time=current_start.isoformat(),
                end_time=current_end.isoformat(),
                recurrence=base_event.recurrence
            )
            events.append(recurring_event)
    
    return events

def format_reminder_message(event: Event) -> str:
    """Format reminder message for an event"""
    time_until = (event.start_time - datetime.now()).total_seconds() / 60
    return f"REMINDER: '{event.title}' starts in {int(time_until)} minutes at {event.start_time.strftime('%H:%M')}"