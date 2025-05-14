from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app import db
from app.models import Pin, Post, Board, Comment

pins_bp = Blueprint('pins', __name__)

@pins_bp.route('/pins/<int:pin_id>')
@login_required
def view_pin(pin_id):
    pin = Pin.query.filter_by(id=pin_id, terminated_at=None).first_or_404()
    post = Post.query.filter_by(id=pin.post_id, terminated_at=None).first_or_404()
    board = Board.query.get_or_404(pin.board_id)
    
    # Get current user's boards for repinning
    current_user_boards = []
    if board.user_id != current_user.id:
        current_user_boards = Board.query.filter_by(
            user_id=current_user.id,
            terminated_at=None
        ).all()
    
    return render_template('pins/view_pin.html',
                         post=post,
                         pin=pin,
                         board=board,
                         current_user_boards=current_user_boards,
                         Comment=Comment) 