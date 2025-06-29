# Event Scheduler System

A Flask-based REST API for managing events with features like creation, updating, deletion, search, reminders, and background scheduling.

## Features

- ✅ **Event CRUD Operations**: Create, Read, Update, Delete events
- ✅ **Advanced Event Search**: Search by title, description, date range, and recurrence
- ✅ **Background Reminder System**: Automatic reminders every minute for upcoming events
- ✅ **Event Reminders**: Get upcoming events within specified time
- ✅ **Recurring Events**: Support for daily, weekly, monthly recurrence
- ✅ **Data Persistence**: Events saved to JSON file
- ✅ **Input Validation**: Comprehensive error handling
- ✅ **Unit Testing**: Complete test suite with pytest
- ✅ **REST API**: RESTful endpoints with proper HTTP status codes
- ✅ **Date-based Queries**: Get today's events, this week's events
- ✅ **Scheduler Status**: Monitor background reminder system

## Installation

### Prerequisites

- Python 3.8+
- pip
- Postman (for API testing)

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd event_manager
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

**Start the server**
```bash
python app.py
```

The API will be available at: `http://localhost:5000`

**Note**: The background reminder system will automatically start and check for upcoming events every minute.

## API Documentation

**Base URL**: `http://localhost:5000`

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/api/events` | Get all events (with search/filtering) |
| POST | `/api/events` | Create new event |
| GET | `/api/events/<id>` | Get specific event |
| PUT | `/api/events/<id>` | Update event |
| DELETE | `/api/events/<id>` | Delete event |
| GET | `/api/events/today` | Get today's events |
| GET | `/api/events/week` | Get this week's events |
| GET | `/api/reminders` | Get upcoming reminders |
| GET | `/api/scheduler/status` | Get scheduler status |

### Query Parameters

#### Search and Filtering
- `GET /api/events?search=<query>` - Search events by title/description
- `GET /api/events?start_date=<ISO_DATE>` - Filter events from this date
- `GET /api/events?end_date=<ISO_DATE>` - Filter events until this date
- `GET /api/events?recurrence=<type>` - Filter by recurrence (daily/weekly/monthly)

#### Reminders
- `GET /api/reminders?minutes=<number>` - Get reminders within specified minutes

## API Usage Examples

### 1. Create an Event

**Request:**
```bash
curl -X POST http://localhost:5000/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team Meeting",
    "description": "Weekly team standup",
    "start_time": "2025-01-15T10:00:00",
    "end_time": "2025-01-15T11:00:00",
    "recurrence": "weekly"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Event created successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Team Meeting",
    "description": "Weekly team standup",
    "start_time": "2025-01-15T10:00:00",
    "end_time": "2025-01-15T11:00:00",
    "recurrence": "weekly",
    "created_at": "2025-01-14T15:30:00.123456"
  }
}
```

### 2. Advanced Search

**Search by text:**
```bash
curl "http://localhost:5000/api/events?search=meeting"
```

**Search by date range:**
```bash
curl "http://localhost:5000/api/events?start_date=2025-01-01T00:00:00&end_date=2025-01-31T23:59:59"
```

**Search by recurrence:**
```bash
curl "http://localhost:5000/api/events?recurrence=weekly"
```

**Combined search:**
```bash
curl "http://localhost:5000/api/events?search=meeting&recurrence=weekly&start_date=2025-01-01T00:00:00"
```

### 3. Get Today's Events

**Request:**
```bash
curl http://localhost:5000/api/events/today
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Daily Standup",
      "description": "Daily team standup",
      "start_time": "2025-01-15T09:00:00",
      "end_time": "2025-01-15T09:15:00",
      "recurrence": "daily"
    }
  ],
  "total": 1,
  "date": "2025-01-15"
}
```

### 4. Get This Week's Events

**Request:**
```bash
curl http://localhost:5000/api/events/week
```

### 5. Get Reminders

**Request:**
```bash
curl "http://localhost:5000/api/reminders?minutes=60"
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "event": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Team Meeting",
        "start_time": "2025-01-15T10:00:00"
      },
      "message": "REMINDER: 'Team Meeting' starts in 45 minutes at 10:00",
      "minutes_until": 45
    }
  ],
  "total": 1,
  "check_interval_minutes": 60
}
```

### 6. Get Scheduler Status

**Request:**
```bash
curl http://localhost:5000/api/scheduler/status
```

**Response:**
```json
{
  "success": true,
  "data": {
    "running": true,
    "check_interval": 60,
    "tracked_events": 2
  }
}
```

## Postman Testing

### Import Postman Collection

1. **Download Postman** from [postman.com](https://www.postman.com/downloads/)

2. **Import Collection:**
   - Open Postman
   - Click **"Import"** button (top left)
   - Click **"Upload Files"**
   - Select `Event_Scheduler_API.postman_collection.json` from your project folder
   - Click **"Import"**

3. **Set Up Environment:**
   - Click the **"Environment"** dropdown (top right)
   - Click **"New"** to create a new environment
   - **Name**: "Event Scheduler Local"
   - **Add Variable**:
     - **Variable**: `base_url`
     - **Initial Value**: `http://localhost:5000`
     - **Current Value**: `http://localhost:5000`
   - Click **"Save"**

### Testing Sequence

#### **Step 1: Verify API is Running**
1. Click **"API Information"** in the collection
2. Click **"Send"**
3. **Expected**: 200 OK with API information

#### **Step 2: Create Test Events**
1. Click **"Events"** → **"Create Event"**
2. Click **"Send"**
3. **Expected**: 201 Created with event data
4. **Copy the event ID** from the response

#### **Step 3: Test CRUD Operations**
1. **Get All Events**: Verify your event appears in the list
2. **Get Specific Event**: Use the copied event ID
3. **Update Event**: Modify title/description
4. **Delete Event**: Remove the test event

#### **Step 4: Test Search & Filters**
1. **Search by Text**: Find events containing "meeting"
2. **Filter by Date**: Test date range filtering
3. **Filter by Recurrence**: Test recurrence filtering

#### **Step 5: Test Date-based Queries**
1. **Get Today's Events**: View today's schedule
2. **Get This Week's Events**: View weekly schedule

#### **Step 6: Test Reminders**
1. **Get Upcoming Reminders**: Check for events due soon
2. **Create an event** that starts within the next hour
3. **Watch the console** for background reminders

#### **Step 7: Test System Status**
1. **Get Scheduler Status**: Verify background system is running

### Expected Test Results

| Test | Expected Status | Description |
|------|----------------|-------------|
| API Information | 200 OK | Shows all available endpoints |
| Create Event | 201 Created | Returns event with unique ID |
| Get All Events | 200 OK | Returns array of events |
| Search Events | 200 OK | Returns filtered results |
| Today's Events | 200 OK | Returns today's events only |
| Week's Events | 200 OK | Returns this week's events |
| Reminders | 200 OK | Returns upcoming events |
| Scheduler Status | 200 OK | Shows background system status |

## Background Reminder System

The application includes a background reminder system that:

- **Runs automatically** when the server starts
- **Checks every minute** for upcoming events
- **Displays reminders** in the console for events due within the next hour
- **Tracks events** to avoid duplicate reminders
- **Cleans up** old events automatically

**Example console output:**
```
🔔 REMINDER: 'Team Meeting' starts in 45 minutes at 10:00
   📅 2025-01-15 10:00
   📝 Weekly team standup
   ⏰ Duration: 60 minutes
```

## Testing

### Run Unit Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_events.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Test Categories
- `TestEvent`: Event model tests
- `TestEventService`: Service layer tests
- `TestAPI`: API endpoint tests
- `TestAdvancedSearch`: Advanced search functionality
- `TestDateBasedQueries`: Date-based query tests
- `TestReminderScheduler`: Background scheduler tests
- `TestNewAPIEndpoints`: New endpoint tests

### Manual Testing Checklist
- ✅ API Information loads correctly
- ✅ Can create events with all required fields
- ✅ Can retrieve all events
- ✅ Search functionality works (text, date, recurrence)
- ✅ Date-based queries return correct results
- ✅ Reminders system shows upcoming events
- ✅ Background scheduler is running
- ✅ Can update existing events
- ✅ Can delete events
- ✅ Error handling works for invalid inputs

## Troubleshooting

### Common Issues

#### **Flask Not Found Error**
```bash
ModuleNotFoundError: No module named 'flask'
```
**Solution:**
```bash
# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### **Connection Refused in Postman**
**Solution:**
- Ensure Flask app is running (`python app.py`)
- Check the URL is correct (`http://localhost:5000`)
- Verify no firewall blocking port 5000

#### **404 Not Found Errors**
**Solution:**
- Check the endpoint URL in Postman
- Ensure the Flask app is running
- Verify the route exists in the API

#### **500 Internal Server Error**
**Solution:**
- Check Flask console for error details
- Verify JSON format in request body
- Check for missing required fields

#### **Invalid JSON Errors**
**Solution:**
- Ensure `Content-Type: application/json` header is set
- Check JSON syntax in request body
- Use proper date format: `2025-01-15T10:00:00`

### Debug Mode
The application runs in debug mode by default. Check the console output for detailed error information.

## Data Format

### Event Object Structure
```json
{
  "id": "unique-event-id",
  "title": "Event Title",
  "description": "Event Description",
  "start_time": "2025-01-15T10:00:00",
  "end_time": "2025-01-15T11:00:00",
  "recurrence": "daily|weekly|monthly|null",
  "created_at": "2025-01-14T15:30:00.123456"
}
```

### Search Parameters
- `search`: Text to search in title and description
- `start_date`: ISO format date (e.g., "2025-01-01T00:00:00")
- `end_date`: ISO format date (e.g., "2025-12-31T23:59:59")
- `recurrence`: "daily", "weekly", "monthly", or null

## Error Handling

The API returns consistent error responses:

```json
{
  "success": false,
  "error": "Error message description"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation errors)
- `404`: Not Found
- `500`: Internal Server Error

## Project Structure

```
event_manager/
├── app/
│   ├── __init__.py
│   ├── models.py          # Event model
│   ├── services.py        # Business logic
│   ├── routes.py          # API endpoints
│   ├── utils.py           # Utility functions
│   └── reminder_scheduler.py  # Background reminder system
├── data/
│   └── events.json        # Event storage
├── tests/
│   ├── __init__.py
│   └── test_events.py     # Test suite
├── app.py                 # Application entry point
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── README.md              # This file
└── Event_Scheduler_API.postman_collection.json
```

## Configuration

### Environment Variables
- `SECRET_KEY`: Flask secret key (defaults to 'dev-secret-key')
- `DATA_FILE`: Path to events JSON file
- `DEBUG`: Debug mode (defaults to True)

### Customization
Modify `config.py` to change:
- Data file location
- Debug mode settings
- Secret key

## Performance Considerations

- **Background Scheduler**: Runs every 60 seconds (configurable)
- **Data Persistence**: JSON file-based storage
- **Search Performance**: In-memory filtering for small datasets
- **Memory Usage**: Events loaded into memory on startup

## Security Notes

- **Development Mode**: Application runs in debug mode by default
- **Data Storage**: Events stored in plain JSON (not encrypted)
- **API Access**: No authentication required (development setup)
- **Input Validation**: All inputs validated before processing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the test cases in `tests/test_events.py`
3. Check Flask console output for error details
4. Verify Postman collection setup

## Version History

- **v1.0.0**: Initial release with CRUD operations
- **v1.1.0**: Added advanced search and filtering
- **v1.2.0**: Added background reminder system
- **v1.3.0**: Added date-based queries and scheduler status
