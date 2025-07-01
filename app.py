# TellMeMore/app.py
import os
from dataAccess import create_app # <--- UPDATED IMPORT PATH
from dataAccess.models.postgres_models import db, User, Quota, ChatSession # <--- UPDATED IMPORT PATH (for Flask-Migrate CLI)

# Determine the configuration class based on environment
config_name = os.environ.get('FLASK_CONFIG', 'development')

# Import the appropriate configuration from config.py
from config import Config

if config_name == 'development':
    app = create_app(Config)
# ... (rest of the config_name logic remains the same)
else:
    app = create_app(Config)


# CLI Commands (optional, but useful for development)
@app.cli.command("init_db")
def init_db_command():
    """Initializes the database tables."""
    with app.app_context():
        db.create_all()
    print("Initialized the database.")

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)