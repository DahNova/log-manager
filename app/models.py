from datetime import datetime
from app import db
from flask_login import UserMixin

# Define User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    # Add a relationship to represent a user's changes
    changes = db.relationship('ChangeLog', backref='user', lazy=True)

# Define ChangeLog model
class ChangeLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    ga4_code = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
