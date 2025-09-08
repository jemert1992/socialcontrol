from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

db = SQLAlchemy()

class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    content_type = db.Column(db.String(50), nullable=False)  # 'image' or 'video'
    caption = db.Column(db.Text, nullable=True)
    hashtags = db.Column(db.Text, nullable=True)
    platforms = db.Column(db.String(100), nullable=True)  # JSON string of platforms
    scheduled_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='draft')  # draft, scheduled, posted, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    posted_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'content_type': self.content_type,
            'caption': self.caption,
            'hashtags': self.hashtags,
            'platforms': self.platforms,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'posted_at': self.posted_at.isoformat() if self.posted_at else None
        }

class SocialAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False)  # 'instagram' or 'tiktok'
    username = db.Column(db.String(100), nullable=False)
    access_token = db.Column(db.Text, nullable=True)
    refresh_token = db.Column(db.Text, nullable=True)
    account_id = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'platform': self.platform,
            'username': self.username,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

