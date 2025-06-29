from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from .services import EventService
from .reminder_scheduler import ReminderScheduler
from datetime import datetime, timedelta

def create_app(config_object):
    app = Flask(__name__)
    app.config.from_object(config_object)
    
    # Initialize services
    event_service = EventService(app.config['DATA_FILE'])
    
    # Initialize reminder scheduler
    reminder_scheduler = ReminderScheduler(event_service)
    
    # Start the reminder scheduler
    reminder_scheduler.start()
    
    api = Api(app)
    
    class EventListResource(Resource):
        def get(self):
            """Get all events with advanced search and filtering"""
            try:
                # Get search parameters
                search_query = request.args.get('search')
                start_date = request.args.get('start_date')
                end_date = request.args.get('end_date')
                recurrence = request.args.get('recurrence')
                
                # Use enhanced search if any parameters are provided
                if any([search_query, start_date, end_date, recurrence]):
                    events = event_service.search_events(
                        query=search_query,
                        start_date=start_date,
                        end_date=end_date,
                        recurrence=recurrence
                    )
                else:
                    events = event_service.get_all_events()
                
                return {
                    'success': True,
                    'data': [event.to_dict() for event in events],
                    'total': len(events),
                    'filters_applied': {
                        'search': search_query,
                        'start_date': start_date,
                        'end_date': end_date,
                        'recurrence': recurrence
                    }
                }, 200
            except Exception as e:
                return {'success': False, 'error': str(e)}, 500
        
        def post(self):
            """Create a new event"""
            try:
                data = request.get_json()
                
                # Validate required fields
                required_fields = ['title', 'description', 'start_time', 'end_time']
                for field in required_fields:
                    if field not in data:
                        return {'success': False, 'error': f'Missing required field: {field}'}, 400
                
                event = event_service.create_event(
                    title=data['title'],
                    description=data['description'],
                    start_time=data['start_time'],
                    end_time=data['end_time'],
                    recurrence=data.get('recurrence')
                )
                
                return {
                    'success': True,
                    'message': 'Event created successfully',
                    'data': event.to_dict()
                }, 201
                
            except ValueError as e:
                return {'success': False, 'error': str(e)}, 400
            except Exception as e:
                return {'success': False, 'error': str(e)}, 500
    
    class EventResource(Resource):
        def get(self, event_id):
            """Get a specific event"""
            try:
                event = event_service.get_event_by_id(event_id)
                if not event:
                    return {'success': False, 'error': 'Event not found'}, 404
                
                return {
                    'success': True,
                    'data': event.to_dict()
                }, 200
            except Exception as e:
                return {'success': False, 'error': str(e)}, 500
        
        def put(self, event_id):
            """Update an event"""
            try:
                data = request.get_json()
                event = event_service.update_event(event_id, **data)
                
                if not event:
                    return {'success': False, 'error': 'Event not found'}, 404
                
                return {
                    'success': True,
                    'message': 'Event updated successfully',
                    'data': event.to_dict()
                }, 200
                
            except ValueError as e:
                return {'success': False, 'error': str(e)}, 400
            except Exception as e:
                return {'success': False, 'error': str(e)}, 500
        
        def delete(self, event_id):
            """Delete an event"""
            try:
                deleted = event_service.delete_event(event_id)
                if not deleted:
                    return {'success': False, 'error': 'Event not found'}, 404
                
                return {
                    'success': True,
                    'message': 'Event deleted successfully'
                }, 200
            except Exception as e:
                return {'success': False, 'error': str(e)}, 500
    
    class ReminderResource(Resource):
        def get(self):
            """Get upcoming reminders"""
            try:
                minutes = request.args.get('minutes', 60, type=int)
                upcoming_events = event_service.get_upcoming_reminders(minutes)
                
                reminders = []
                for event in upcoming_events:
                    time_until = (event.start_time - datetime.now()).total_seconds() / 60
                    message = f"REMINDER: '{event.title}' starts in {int(time_until)} minutes at {event.start_time.strftime('%H:%M')}"
                    reminders.append({
                        'event': event.to_dict(),
                        'message': message,
                        'minutes_until': int(time_until)
                    })
                
                return {
                    'success': True,
                    'data': reminders,
                    'total': len(reminders),
                    'check_interval_minutes': minutes
                }, 200
            except Exception as e:
                return {'success': False, 'error': str(e)}, 500
    
    class TodayEventsResource(Resource):
        def get(self):
            """Get all events scheduled for today"""
            try:
                today_events = event_service.get_today_events()
                
                return {
                    'success': True,
                    'data': [event.to_dict() for event in today_events],
                    'total': len(today_events),
                    'date': datetime.now().date().isoformat()
                }, 200
            except Exception as e:
                return {'success': False, 'error': str(e)}, 500
    
    class WeekEventsResource(Resource):
        def get(self):
            """Get all events scheduled for the current week"""
            try:
                week_events = event_service.get_week_events()
                
                return {
                    'success': True,
                    'data': [event.to_dict() for event in week_events],
                    'total': len(week_events),
                    'week_start': (datetime.now().date() - timedelta(days=datetime.now().weekday())).isoformat()
                }, 200
            except Exception as e:
                return {'success': False, 'error': str(e)}, 500
    
    class SchedulerStatusResource(Resource):
        def get(self):
            """Get the status of the reminder scheduler"""
            try:
                status = reminder_scheduler.get_status()
                
                return {
                    'success': True,
                    'data': status
                }, 200
            except Exception as e:
                return {'success': False, 'error': str(e)}, 500
    
    api.add_resource(EventListResource, '/api/events')
    api.add_resource(EventResource, '/api/events/<string:event_id>')
    api.add_resource(ReminderResource, '/api/reminders')
    api.add_resource(TodayEventsResource, '/api/events/today')
    api.add_resource(WeekEventsResource, '/api/events/week')
    api.add_resource(SchedulerStatusResource, '/api/scheduler/status')
    
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Event Scheduler API',
            'version': '1.0.0',
            'endpoints': {
                'GET /api/events': 'Get all events (with search/filtering)',
                'POST /api/events': 'Create event',
                'GET /api/events/<id>': 'Get specific event',
                'PUT /api/events/<id>': 'Update event',
                'DELETE /api/events/<id>': 'Delete event',
                'GET /api/events/today': 'Get today\'s events',
                'GET /api/events/week': 'Get this week\'s events',
                'GET /api/reminders': 'Get upcoming reminders',
                'GET /api/scheduler/status': 'Get scheduler status'
            },
            'search_parameters': {
                'search': 'Search in title and description',
                'start_date': 'Filter events from this date (ISO format)',
                'end_date': 'Filter events until this date (ISO format)',
                'recurrence': 'Filter by recurrence type (daily/weekly/monthly)'
            }
        })
    
    return app