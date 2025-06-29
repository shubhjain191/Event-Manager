import pytest
import json
import tempfile
import os
from datetime import datetime, timedelta
from app.models import Event
from app.services import EventService
from app.routes import create_app
from config import Config

class TestConfig(Config):
    TESTING = True
    
@pytest.fixture
def temp_data_file():
    """Create a temporary data file for testing"""
    fd, path = tempfile.mkstemp(suffix='.json')
    os.close(fd)
    yield path
    os.unlink(path)

@pytest.fixture
def event_service(temp_data_file):
    """Create an EventService instance with temporary data file"""
    return EventService(temp_data_file)

@pytest.fixture
def client(temp_data_file):
    """Create a test client"""
    config = TestConfig()
    config.DATA_FILE = temp_data_file
    app = create_app(config)
    app.config['TESTING'] = True
    return app.test_client()

@pytest.fixture
def sample_event_data():
    """Sample event data for testing"""
    future_time = datetime.now() + timedelta(hours=2)
    return {
        'title': 'Test Event',
        'description': 'Test Description',
        'start_time': future_time.isoformat(),
        'end_time': (future_time + timedelta(hours=1)).isoformat()
    }

class TestEvent:
    def test_event_creation(self):
        """Test event creation"""
        future_time = datetime.now() + timedelta(hours=2)
        event = Event(
            title="Test Event",
            description="Test Description",
            start_time=future_time.isoformat(),
            end_time=(future_time + timedelta(hours=1)).isoformat()
        )
        
        assert event.title == "Test Event"
        assert event.description == "Test Description"
        assert event.id is not None
        assert event.start_time < event.end_time
    
    def test_invalid_time_range(self):
        """Test that invalid time ranges raise ValueError"""
        future_time = datetime.now() + timedelta(hours=2)
        
        with pytest.raises(ValueError):
            Event(
                title="Test Event",
                description="Test Description",
                start_time=(future_time + timedelta(hours=1)).isoformat(),
                end_time=future_time.isoformat()  # End before start
            )
    
    def test_event_serialization(self):
        """Test event to_dict and from_dict methods"""
        future_time = datetime.now() + timedelta(hours=2)
        original_event = Event(
            title="Test Event",
            description="Test Description",
            start_time=future_time.isoformat(),
            end_time=(future_time + timedelta(hours=1)).isoformat()
        )
        
        event_dict = original_event.to_dict()
        recreated_event = Event.from_dict(event_dict)
        
        assert recreated_event.title == original_event.title
        assert recreated_event.description == original_event.description
        assert recreated_event.id == original_event.id

class TestEventService:
    def test_create_event(self, event_service):
        """Test event creation through service"""
        future_time = datetime.now() + timedelta(hours=2)
        event = event_service.create_event(
            title="Service Test Event",
            description="Service Test Description",
            start_time=future_time.isoformat(),
            end_time=(future_time + timedelta(hours=1)).isoformat()
        )
        
        assert event.title == "Service Test Event"
        assert len(event_service.events) == 1
    
    def test_get_all_events(self, event_service):
        """Test getting all events"""
        # Create multiple events
        base_time = datetime.now() + timedelta(hours=1)
        for i in range(3):
            event_service.create_event(
                title=f"Event {i}",
                description=f"Description {i}",
                start_time=(base_time + timedelta(hours=i)).isoformat(),
                end_time=(base_time + timedelta(hours=i+1)).isoformat()
            )
        
        events = event_service.get_all_events()
        assert len(events) == 3
        
        # Check if sorted by time
        for i in range(len(events) - 1):
            assert events[i].start_time <= events[i + 1].start_time
    
    def test_update_event(self, event_service):
        """Test event updating"""
        future_time = datetime.now() + timedelta(hours=2)
        event = event_service.create_event(
            title="Original Title",
            description="Original Description",
            start_time=future_time.isoformat(),
            end_time=(future_time + timedelta(hours=1)).isoformat()
        )
        
        updated_event = event_service.update_event(
            event.id,
            title="Updated Title"
        )
        
        assert updated_event.title == "Updated Title"
        assert updated_event.description == "Original Description"
    
    def test_delete_event(self, event_service):
        """Test event deletion"""
        future_time = datetime.now() + timedelta(hours=2)
        event = event_service.create_event(
            title="To Be Deleted",
            description="Description",
            start_time=future_time.isoformat(),
            end_time=(future_time + timedelta(hours=1)).isoformat()
        )
        
        assert len(event_service.events) == 1
        
        deleted = event_service.delete_event(event.id)
        assert deleted is True
        assert len(event_service.events) == 0
    
    def test_search_events(self, event_service):
        """Test event searching"""
        future_time = datetime.now() + timedelta(hours=2)
        
        # Create events with different titles and descriptions
        event_service.create_event(
            title="Meeting with Client",
            description="Important business meeting",
            start_time=future_time.isoformat(),
            end_time=(future_time + timedelta(hours=1)).isoformat()
        )
        
        event_service.create_event(
            title="Doctor Appointment",
            description="Regular checkup",
            start_time=(future_time + timedelta(hours=2)).isoformat(),
            end_time=(future_time + timedelta(hours=3)).isoformat()
        )
        
        # Search by title
        meeting_events = event_service.search_events("meeting")
        assert len(meeting_events) == 1
        assert "Meeting" in meeting_events[0].title
        
        # Search by description
        business_events = event_service.search_events("business")
        assert len(business_events) == 1

class TestAPI:
    def test_create_event_api(self, client, sample_event_data):
        """Test event creation via API"""
        response = client.post('/api/events', 
                             data=json.dumps(sample_event_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['title'] == sample_event_data['title']
    
    def test_get_events_api(self, client, sample_event_data):
        """Test getting events via API"""
        # First create an event
        client.post('/api/events', 
                   data=json.dumps(sample_event_data),
                   content_type='application/json')
        
        # Then get all events
        response = client.get('/api/events')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']) == 1
    
    def test_update_event_api(self, client, sample_event_data):
        """Test event updating via API"""
        # Create event
        create_response = client.post('/api/events', 
                                    data=json.dumps(sample_event_data),
                                    content_type='application/json')
        event_id = json.loads(create_response.data)['data']['id']
        
        # Update event
        update_data = {'title': 'Updated Title'}
        response = client.put(f'/api/events/{event_id}',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['title'] == 'Updated Title'
    
    def test_delete_event_api(self, client, sample_event_data):
        """Test event deletion via API"""
        # Create event
        create_response = client.post('/api/events', 
                                    data=json.dumps(sample_event_data),
                                    content_type='application/json')
        event_id = json.loads(create_response.data)['data']['id']
        
        # Delete event
        response = client.delete(f'/api/events/{event_id}')
        assert response.status_code == 200
        
        # Verify deletion
        get_response = client.get(f'/api/events/{event_id}')
        assert get_response.status_code == 404
    
    def test_invalid_event_data(self, client):
        """Test API with invalid event data"""
        invalid_data = {
            'title': 'Test Event',
            # Missing required fields
        }
        
        response = client.post('/api/events',
                             data=json.dumps(invalid_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False

class TestAdvancedSearch:
    def test_search_by_date_range(self, event_service):
        """Test searching events by date range"""
        # Create events on different dates
        base_time = datetime.now()
        
        # Event 1: Today
        event_service.create_event(
            title="Today's Event",
            description="Event today",
            start_time=base_time.isoformat(),
            end_time=(base_time + timedelta(hours=1)).isoformat()
        )
        
        # Event 2: Tomorrow
        tomorrow = base_time + timedelta(days=1)
        event_service.create_event(
            title="Tomorrow's Event",
            description="Event tomorrow",
            start_time=tomorrow.isoformat(),
            end_time=(tomorrow + timedelta(hours=1)).isoformat()
        )
        
        # Event 3: Next week
        next_week = base_time + timedelta(days=7)
        event_service.create_event(
            title="Next Week's Event",
            description="Event next week",
            start_time=next_week.isoformat(),
            end_time=(next_week + timedelta(hours=1)).isoformat()
        )
        
        # Search for events in the next 3 days
        end_date = (base_time + timedelta(days=3)).isoformat()
        events = event_service.search_events(end_date=end_date)
        
        assert len(events) == 2  # Today's and tomorrow's events
        assert any("Today's Event" in event.title for event in events)
        assert any("Tomorrow's Event" in event.title for event in events)
        assert not any("Next Week's Event" in event.title for event in events)
    
    def test_search_by_recurrence(self, event_service):
        """Test searching events by recurrence type"""
        future_time = datetime.now() + timedelta(hours=1)
        
        # Create events with different recurrence types
        event_service.create_event(
            title="Daily Meeting",
            description="Daily standup",
            start_time=future_time.isoformat(),
            end_time=(future_time + timedelta(hours=1)).isoformat(),
            recurrence="daily"
        )
        
        event_service.create_event(
            title="Weekly Review",
            description="Weekly team review",
            start_time=(future_time + timedelta(hours=2)).isoformat(),
            end_time=(future_time + timedelta(hours=3)).isoformat(),
            recurrence="weekly"
        )
        
        event_service.create_event(
            title="One-time Event",
            description="One-time meeting",
            start_time=(future_time + timedelta(hours=4)).isoformat(),
            end_time=(future_time + timedelta(hours=5)).isoformat()
        )
        
        # Search for daily events
        daily_events = event_service.search_events(recurrence="daily")
        assert len(daily_events) == 1
        assert daily_events[0].title == "Daily Meeting"
        
        # Search for weekly events
        weekly_events = event_service.search_events(recurrence="weekly")
        assert len(weekly_events) == 1
        assert weekly_events[0].title == "Weekly Review"
        
        # Search for non-recurring events
        one_time_events = event_service.search_events(recurrence=None)
        assert len(one_time_events) == 1
        assert one_time_events[0].title == "One-time Event"
    
    def test_combined_search(self, event_service):
        """Test combining multiple search filters"""
        future_time = datetime.now() + timedelta(hours=1)
        
        # Create events with different characteristics
        event_service.create_event(
            title="Team Meeting",
            description="Weekly team meeting",
            start_time=future_time.isoformat(),
            end_time=(future_time + timedelta(hours=1)).isoformat(),
            recurrence="weekly"
        )
        
        event_service.create_event(
            title="Client Meeting",
            description="Meeting with client",
            start_time=(future_time + timedelta(hours=2)).isoformat(),
            end_time=(future_time + timedelta(hours=3)).isoformat()
        )
        
        # Search for weekly events containing "meeting"
        events = event_service.search_events(
            query="meeting",
            recurrence="weekly"
        )
        
        assert len(events) == 1
        assert events[0].title == "Team Meeting"

class TestDateBasedQueries:
    def test_get_today_events(self, event_service):
        """Test getting today's events"""
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        # Create events for today and tomorrow
        today_time = datetime.combine(today, datetime.min.time()) + timedelta(hours=10)
        tomorrow_time = datetime.combine(tomorrow, datetime.min.time()) + timedelta(hours=10)
        
        event_service.create_event(
            title="Today's Event",
            description="Event today",
            start_time=today_time.isoformat(),
            end_time=(today_time + timedelta(hours=1)).isoformat()
        )
        
        event_service.create_event(
            title="Tomorrow's Event",
            description="Event tomorrow",
            start_time=tomorrow_time.isoformat(),
            end_time=(tomorrow_time + timedelta(hours=1)).isoformat()
        )
        
        today_events = event_service.get_today_events()
        assert len(today_events) == 1
        assert today_events[0].title == "Today's Event"
    
    def test_get_week_events(self, event_service):
        """Test getting this week's events"""
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        
        # Create events for this week and next week
        this_week_time = datetime.combine(week_start + timedelta(days=2), datetime.min.time()) + timedelta(hours=10)
        next_week_time = datetime.combine(week_start + timedelta(days=8), datetime.min.time()) + timedelta(hours=10)
        
        event_service.create_event(
            title="This Week's Event",
            description="Event this week",
            start_time=this_week_time.isoformat(),
            end_time=(this_week_time + timedelta(hours=1)).isoformat()
        )
        
        event_service.create_event(
            title="Next Week's Event",
            description="Event next week",
            start_time=next_week_time.isoformat(),
            end_time=(next_week_time + timedelta(hours=1)).isoformat()
        )
        
        week_events = event_service.get_week_events()
        assert len(week_events) == 1
        assert week_events[0].title == "This Week's Event"

class TestReminderScheduler:
    def test_scheduler_initialization(self, event_service):
        """Test reminder scheduler initialization"""
        from app.reminder_scheduler import ReminderScheduler
        
        scheduler = ReminderScheduler(event_service)
        assert scheduler.event_service == event_service
        assert scheduler.check_interval == 60
        assert scheduler.running == False
    
    def test_scheduler_status(self, event_service):
        """Test scheduler status method"""
        from app.reminder_scheduler import ReminderScheduler
        
        scheduler = ReminderScheduler(event_service)
        status = scheduler.get_status()
        
        assert 'running' in status
        assert 'check_interval' in status
        assert 'tracked_events' in status
        assert status['running'] == False
        assert status['check_interval'] == 60
        assert status['tracked_events'] == 0

class TestNewAPIEndpoints:
    def test_get_today_events_api(self, client, sample_event_data):
        """Test getting today's events via API"""
        # Create an event for today
        today = datetime.now().date()
        today_time = datetime.combine(today, datetime.min.time()) + timedelta(hours=10)
        
        event_data = sample_event_data.copy()
        event_data['start_time'] = today_time.isoformat()
        event_data['end_time'] = (today_time + timedelta(hours=1)).isoformat()
        
        # Create the event
        client.post('/api/events',
                   data=json.dumps(event_data),
                   content_type='application/json')
        
        # Get today's events
        response = client.get('/api/events/today')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']) >= 1
        assert 'date' in data
    
    def test_get_week_events_api(self, client, sample_event_data):
        """Test getting this week's events via API"""
        # Create an event for this week
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        this_week_time = datetime.combine(week_start + timedelta(days=2), datetime.min.time()) + timedelta(hours=10)
        
        event_data = sample_event_data.copy()
        event_data['start_time'] = this_week_time.isoformat()
        event_data['end_time'] = (this_week_time + timedelta(hours=1)).isoformat()
        
        # Create the event
        client.post('/api/events',
                   data=json.dumps(event_data),
                   content_type='application/json')
        
        # Get this week's events
        response = client.get('/api/events/week')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']) >= 1
        assert 'week_start' in data
    
    def test_advanced_search_api(self, client, sample_event_data):
        """Test advanced search via API"""
        # Create an event
        client.post('/api/events',
                   data=json.dumps(sample_event_data),
                   content_type='application/json')
        
        # Search with query parameter
        response = client.get('/api/events?search=Test')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'filters_applied' in data
        assert data['filters_applied']['search'] == 'Test'
    
    def test_scheduler_status_api(self, client):
        """Test getting scheduler status via API"""
        response = client.get('/api/scheduler/status')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert 'running' in data['data']

if __name__ == '__main__':
    pytest.main([__file__])