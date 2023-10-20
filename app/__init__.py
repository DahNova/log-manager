from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Set a secret key
    app.config['SECRET_KEY'] = 'your_secret_key_here'

    # Configure the database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:root@localhost/changelog_db'
    
    # Initialize the database with the app
    db.init_app(app)
    migrate = Migrate(app, db)
    with app.app_context():
        try:
            # Attempt to establish a connection and create a cursor
            db.engine.execute("SELECT 1")
        except Exception as e:
            # Handle the error (e.g., print or log the error message)
            print(f"Database connection error: {str(e)}")
            print(f"SQLAlchemy Configuration: {app.config}")

    from .routes import init_app
    init_app(app, db)

    return app
