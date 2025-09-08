from src.models.user import db
from datetime import datetime

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    discord_message_id = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    avatar_url = db.Column(db.String(500))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, nullable=False)
    channel_id = db.Column(db.String(50), nullable=False)
    channel_name = db.Column(db.String(100), nullable=False)
    server_id = db.Column(db.String(50), nullable=False)
    server_name = db.Column(db.String(100), nullable=False)
    message_type = db.Column(db.String(20), default='text')  # 'text', 'image', 'audio', 'embed'
    media_url = db.Column(db.String(500))
    media_filename = db.Column(db.String(200))
    is_bot = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Message {self.discord_message_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'discord_message_id': self.discord_message_id,
            'user_id': self.user_id,
            'username': self.username,
            'avatar_url': self.avatar_url,
            'content': self.content,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'channel_id': self.channel_id,
            'channel_name': self.channel_name,
            'server_id': self.server_id,
            'server_name': self.server_name,
            'message_type': self.message_type,
            'media_url': self.media_url,
            'media_filename': self.media_filename,
            'is_bot': self.is_bot,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Channel(db.Model):
    __tablename__ = 'channels'
    
    id = db.Column(db.Integer, primary_key=True)
    discord_channel_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    server_id = db.Column(db.String(50), nullable=False)
    server_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Channel {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'discord_channel_id': self.discord_channel_id,
            'name': self.name,
            'server_id': self.server_id,
            'server_name': self.server_name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

