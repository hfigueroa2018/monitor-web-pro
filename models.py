from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sites = db.relationship('Site', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    chat_ids = db.Column(db.Text, default='[]')  # JSON list
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    metrics = db.relationship('Metric', backref='site', lazy=True)

    def get_chat_ids(self):
        try:
            return json.loads(self.chat_ids)
        except:
            return []

    def set_chat_ids(self, chat_ids):
        self.chat_ids = json.dumps(chat_ids or [])

    def __repr__(self):
        return f'<Site {self.url}>'

class Metric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'), nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(10), nullable=False)  # 'up' or 'down'
    response_time_ms = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'<Metric {self.site.url} {self.status} {self.time}>'