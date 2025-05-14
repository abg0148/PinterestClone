from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import and_

from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    full_name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    bio = db.Column(db.Text)
    picture = db.Column(db.LargeBinary)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    terminated_at = db.Column(db.DateTime)

    # Add relationships
    boards = db.relationship('Board', backref='user', lazy='dynamic')
    likes = db.relationship('Like', backref='user', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    follow_streams = db.relationship('FollowStream', backref='user', lazy='dynamic')

    def get_id(self):
        return str(self.id)

    def is_friend_with(self, user_id):
        """Check if this user is friends with another user."""
        # For now, everyone is friends with everyone
        return True

    def create_default_board(self):
        """Create a default board for new users."""
        default_board = Board(
            user_id=self.id,
            board_name="Unorganized Ideas",
            description="A place for your unorganized pins and ideas",
            allow_public_comments=True
        )
        db.session.add(default_board)
        db.session.commit()
        return default_board


class Board(db.Model):
    __tablename__ = 'board'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    board_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    allow_public_comments = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    terminated_at = db.Column(db.DateTime)

    # Add relationships
    pins = db.relationship('Pin', backref='board', lazy='dynamic')

    def get_last_pin_image(self):
        """Get the image URL of the last pinned post."""
        last_pin = (
            self.pins
            .filter_by(terminated_at=None)
            .order_by(Pin.created_at.desc())
            .first()
        )
        if last_pin and last_pin.post:
            return last_pin.post.image_url
        return None

    def get_pin_count(self):
        """Get the number of active pins in this board."""
        return self.pins.filter_by(terminated_at=None).count()


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

    # Add relationships
    likes = db.relationship('Like', backref='post', lazy='dynamic')
    pins = db.relationship('Pin', backref='post', lazy='dynamic')
    author = db.relationship('User', backref='posts')


class Pin(db.Model):
    __tablename__ = 'pin'

    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    root_pin_id = db.Column(db.Integer, db.ForeignKey('pin.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    terminated_at = db.Column(db.DateTime)

    # Add relationships
    comments = db.relationship('Comment', backref='pin', lazy='dynamic')
    repins = db.relationship('Pin',
                           backref=db.backref('source_pin', remote_side=[id]),
                           lazy='dynamic')

    def delete(self):
        """
        Soft delete a pin and its related data based on whether it's a root pin or repin.
        If it's a root pin:
            - Soft delete all repins
            - Soft delete the associated post
            - Soft delete this pin
        If it's a repin:
            - Only soft delete this pin
        """
        now = datetime.utcnow()
        
        if self.root_pin_id is None:  # This is a root pin
            # Soft delete all repins
            for repin in self.repins.filter_by(terminated_at=None).all():
                repin.terminated_at = now
            
            # Soft delete the associated post
            if self.post and not self.post.terminated_at:
                self.post.terminated_at = now
        
        # Soft delete this pin
        self.terminated_at = now
        db.session.commit()


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

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True, nullable=False)
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

    __table_args__ = (
        db.CheckConstraint('user_id_1 < user_id_2', name='friend_check'),
    )


class FollowStream(db.Model):
    __tablename__ = 'follow_stream'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stream_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    terminated_at = db.Column(db.DateTime)

    # Relationships
    boards = db.relationship('Board', 
                           secondary='follow_stream_board',
                           primaryjoin="and_(FollowStream.id==FollowStreamBoard.stream_id, FollowStreamBoard.deleted_at==None)",
                           secondaryjoin="Board.id==FollowStreamBoard.board_id",
                           lazy='dynamic',
                           backref=db.backref('follow_streams', lazy='dynamic'))

    def get_last_pin(self):
        """Get the most recent pin from any board in this stream."""
        from app.models import Pin, Post  # Import here to avoid circular imports
        
        # Get all active board IDs in this stream
        board_ids = [board.id for board in self.boards.all()]
        
        if not board_ids:
            return None
            
        # Find the most recent pin from any of these boards
        return Pin.query.join(Post).filter(
            Pin.board_id.in_(board_ids),
            Pin.terminated_at == None,
            Post.terminated_at == None
        ).order_by(Post.created_at.desc()).first()


class FollowStreamBoard(db.Model):
    __tablename__ = 'follow_stream_board'

    stream_id = db.Column(db.Integer, db.ForeignKey('follow_stream.id'), primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('board.id'), primary_key=True)
    deleted_at = db.Column(db.DateTime)

    # Add relationships
    board = db.relationship('Board', backref=db.backref('stream_boards', lazy='dynamic'))
