from flask_sqlalchemy import SQLAlchemy
import uuid

db = SQLAlchemy()

def generate_code():
    return str(uuid.uuid4())[:8]  # 8-character short code

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    unique_code = db.Column(db.String(20), unique=True, default=generate_code)

class FileShare(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    filename = db.Column(db.String(200))
    filepath = db.Column(db.String(300))
