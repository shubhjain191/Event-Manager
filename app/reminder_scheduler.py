import threading
import time
from datetime import datetime, timedelta
from typing import List
from .services import EventService
from .utils import format_reminder_message

class ReminderScheduler:
    def __init__(self, event_service: EventService, check_interval: int = 60):
        """
        Initialize the reminder scheduler
        
        Args:
            event_service: EventService instance
            check_interval: Check interval in seconds (default: 60 seconds)
        """
        self.event_service = event_service
        self.check_interval = check_interval
        self.running = False
        self.thread = None
        self.last_checked_events = set()  # Track events we've already reminded about
    
    def start(self):
        """Start the reminder scheduler in a background thread"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print(f"Reminder scheduler started. Checking every {self.check_interval} seconds.")
    
    def stop(self):
        """Stop the reminder scheduler"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("Reminder scheduler stopped.")
    
    def _run(self):
        """Main loop for checking reminders"""
        while self.running:
            try:
                self._check_reminders()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"Error in reminder scheduler: {e}")
                time.sleep(self.check_interval)
    
    def _check_reminders(self):
        """Check for upcoming events and display reminders"""
        upcoming_events = self.event_service.get_upcoming_reminders(minutes=60)
        current_time = datetime.now()
        
        for event in upcoming_events:
            # Only show reminder if we haven't shown it recently
            if event.id not in self.last_checked_events:
                time_until = (event.start_time - current_time).total_seconds() / 60
                
                if 0 <= time_until <= 60: 
                    message = format_reminder_message(event)
                    print(f"\n🔔 {message}")
                    print(f"   📅 {event.start_time.strftime('%Y-%m-%d %H:%M')}")
                    print(f"   📝 {event.description}")
                    print(f"   ⏰ Duration: {(event.end_time - event.start_time).total_seconds() / 60:.0f} minutes")
                    
                    # Mark this event as checked
                    self.last_checked_events.add(event.id)
        
        # Clean up old events from tracking (events that have passed)
        self._cleanup_old_events()
    
    def _cleanup_old_events(self):
        """Remove events that have already passed from tracking"""
        current_time = datetime.now()
        events_to_remove = set()
        
        for event_id in self.last_checked_events:
            event = self.event_service.get_event_by_id(event_id)
            if event and event.start_time < current_time:
                events_to_remove.add(event_id)
        
        self.last_checked_events -= events_to_remove
    
    def get_status(self) -> dict:
        """Get the current status of the scheduler"""
        return {
            'running': self.running,
            'check_interval': self.check_interval,
            'tracked_events': len(self.last_checked_events)
        } 