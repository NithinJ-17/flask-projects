from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(100), nullable=False)
    due_date = db.Column(db.Date, nullable=True)  # Changed to Date type
    
    def __repr__(self):
        return f'<Task {self.id}>'
