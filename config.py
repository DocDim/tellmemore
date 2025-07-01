# TellMeMore/config.py
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'f7bd3a1f57a9ce1e2bc3e054fe8a2e95a3011c02eec49aa3b4936ef7133b8ff7')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'f7bd3a1f57a9ce1e2bc3e054fe8a2e95a3011c02eec49aa3b4936ef7133b8ff7')

    # PostgreSQL Configuration
    # Fallback to a default if DATABASE_URL not set in .env or environment
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') 
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Suppresses a warning

    # MongoDB Configuration
    # Fallback to a default if MONGO_URI not set in .env or environment
    MONGO_URI = os.environ.get('MONGO_URI') 

    CORS_HEADERS = 'Content-Type' # Default CORS headers

class DevelopmentConfig(Config):
    DEBUG = True
    # If you want different local development URLs:
    # SQLALCHEMY_DATABASE_URI = 'postgresql://dev_user:dev_password@localhost:5432/tellmemore_dev_db'
    # MONGO_URI = 'mongodb://localhost:27017/tellmemore_dev_mongo_db'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') 
    MONGO_URI = os.environ.get('MONGO_URI') 

class TestingConfig(Config):
    TESTING = True
    # Use dedicated test databases
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') 
    MONGO_URI = os.environ.get('MONGO_URI') 

class ProductionConfig(Config):
    DEBUG = False
    # Ensure these are always set as environment variables in production
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # MONGO_URI = os.environ.get('MONGO_URI')
    # SECRET_KEY = os.environ.get('SECRET_KEY')
    # JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')