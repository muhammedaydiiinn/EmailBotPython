from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class EmailHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    error_message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    smtp_server = db.Column(db.String(255), nullable=False)
    smtp_port = db.Column(db.Integer, nullable=False)
    smtp_username = db.Column(db.String(255), nullable=False)
    smtp_password = db.Column(db.String(255), nullable=False)
    sender_email = db.Column(db.String(255), nullable=False)
    sender_name = db.Column(db.String(255), nullable=False, default="İK Ekibi")
    email_subject = db.Column(db.String(255), nullable=False)
    email_body = db.Column(db.Text, nullable=False)
    attachment_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)