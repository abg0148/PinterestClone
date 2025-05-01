from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    bio = db.Column(db.Text)
    picture = db.Column(db.LargeBinary)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    terminated_at = db.Column(db.DateTime)

    def get_id(self):
        return str(self.id)


class Board(db.Model):
    __tablename__ = 'board'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    board_name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    allow_public_comments = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    terminated_at = db.Column(db.DateTime)

    __table_args__ = (db.UniqueConstraint('user_id', 'board_name'),)


class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tags = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, unique=True, nullable=False)
    source_page = db.Column(db.Text)
    image_blob = db.Column(db.LargeBinary)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    terminated_at = db.Column(db.DateTime)


class Pin(db.Model):
    __tablename__ = 'pin'

    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    root_pin_id = db.Column(db.Integer, db.ForeignKey('pin.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    terminated_at = db.Column(db.DateTime)

    __table_args__ = (db.UniqueConstraint('board_id', 'post_id'),)


class Comment(db.Model):
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    pin_id = db.Column(db.Integer, db.ForeignKey('pin.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)


class Like(db.Model):
    __tablename__ = 'like'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    terminated_at = db.Column(db.DateTime)


class FriendRequest(db.Model):
    __tablename__ = 'friend_request'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    terminated_at = db.Column(db.DateTime)


class Friend(db.Model):
    __tablename__ = 'friend'

    user_id_1 = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user_id_2 = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    since = db.Column(db.DateTime, default=datetime.utcnow)
    terminated_at = db.Column(db.DateTime)


class FollowStream(db.Model):
    __tablename__ = 'follow_stream'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stream_name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    terminated_at = db.Column(db.DateTime)


class FollowStreamBoard(db.Model):
    __tablename__ = 'follow_stream_board'

    stream_id = db.Column(db.Integer, db.ForeignKey('follow_stream.id'), primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'), primary_key=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)
