import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'jeopardy-secret-key-change-in-production'
    PORT = 9001
    HOST = '0.0.0.0'  # Allow connections from any device on local network
    DEBUG = True
    QUESTIONS_FILE = 'data/questions.csv'
    BUZZ_DELAY_SECONDS = 4