from flask import Blueprint, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Like, Comment, Post, Pin, Board, User
from datetime import datetime
from sqlalchemy import and_

social_bp = Blueprint('social', __name__)

@social_bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def toggle_like(post_id):
    post = Post.query.get_or_404(post_id)
    
    try:
        # Find existing active like
        existing_like = Like.query.filter(
            and_(
                Like.user_id == current_user.id,
                Like.post_id == post_id,
                Like.terminated_at.is_(None)
            )
        ).first()

        if existing_like:
            # Unlike - just mark as terminated
            existing_like.terminated_at = datetime.utcnow()
            db.session.commit()
            flash("Post unliked successfully!", "success")
        else:
            # Check if there's a terminated like we can reuse
            terminated_like = Like.query.filter(
                and_(
                    Like.user_id == current_user.id,
                    Like.post_id == post_id,
                    Like.terminated_at.isnot(None)
                )
            ).first()

            if terminated_like:
                # Reuse the terminated like by removing termination
                terminated_like.terminated_at = None
                terminated_like.created_at = datetime.utcnow()
            else:
                # Create new like
                new_like = Like(user_id=current_user.id, post_id=post_id)
                db.session.add(new_like)
            
            db.session.commit()
            flash("Post liked successfully!", "success")

    except Exception as e:
        db.session.rollback()
        flash("Error updating like status.", "error")
        print(f"Like error: {str(e)}")

    # Get the board_id to redirect back to the board view
    pin = Pin.query.filter_by(post_id=post_id, terminated_at=None).first()
    if pin:
        return redirect(url_for('boards.view_board', board_id=pin.board_id))
    return redirect(url_for('dashboard.dashboard'))

@social_bp.route('/pin/<int:pin_id>/comment', methods=['POST'])
@login_required
def add_comment(pin_id):
    pin = Pin.query.get_or_404(pin_id)
    board = Board.query.get_or_404(pin.board_id)
    
    # Check if comments are allowed
    can_comment = (
        board.allow_public_comments or  # Public comments allowed
        board.user_id == current_user.id or  # Board owner
        current_user.is_friend_with(board.user_id)  # Friends can always comment
    )
    
    if not can_comment:
        flash("Comments are not allowed on this board.", "error")
        return redirect(url_for('boards.view_board', board_id=board.id))

    comment_text = request.form.get('comment', '').strip()
    if not comment_text:
        flash("Comment cannot be empty.", "error")
        return redirect(url_for('boards.view_board', board_id=board.id))

    new_comment = Comment(
        pin_id=pin_id,
        user_id=current_user.id,
        body=comment_text
    )
    
    try:
        db.session.add(new_comment)
        db.session.commit()
        flash("Comment added successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error adding comment.", "error")
        print(e)

    return redirect(url_for('boards.view_board', board_id=board.id))

@social_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    # Only allow comment author or board owner to delete comments
    pin = Pin.query.get_or_404(comment.pin_id)
    board = Board.query.get_or_404(pin.board_id)
    
    if comment.user_id != current_user.id and board.user_id != current_user.id:
        flash("You don't have permission to delete this comment.", "error")
        return redirect(url_for('boards.view_board', board_id=board.id))

    try:
        comment.deleted_at = datetime.utcnow()
        db.session.commit()
        flash("Comment deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error deleting comment.", "error")
        print(e)

    return redirect(url_for('boards.view_board', board_id=board.id)) 