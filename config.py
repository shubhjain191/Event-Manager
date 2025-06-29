import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'events.json')
    DEBUG = True