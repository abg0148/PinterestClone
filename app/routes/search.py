from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Friend, User, FriendRequest, Post, Pin, Board
from datetime import datetime
from sqlalchemy import or_, and_

search_bp = Blueprint('search', __name__)

@search_bp.route('/profile/search', methods=['GET', 'POST'])
@login_required
def search():
    search_term = request.form.get("identifier", type=str)
    if not search_term:
        flash("Bad Request.", "error")
        return redirect(url_for('dashboard.dashboard'))

    # First try exact username match
    exact_matches = (
        User.query
            .filter(User.username == search_term,
                    User.terminated_at == None,
                    User.id != current_user.id)
            .all()
    )

    # Search for posts by tags
    search_pattern = f"%{search_term}%"
    matching_posts = (
        db.session.query(Post, Pin, Board, User)
        .join(Pin, and_(Post.id == Pin.post_id, Pin.terminated_at == None))
        .join(Board, and_(Pin.board_id == Board.id, Board.terminated_at == None))
        .join(User, and_(Board.user_id == User.id, User.terminated_at == None))
        .filter(
            Post.tags.ilike(search_pattern),
            Post.terminated_at == None
        )
        .order_by(Post.created_at.desc())
        .all()
    )

    # Get current user's boards for repinning
    current_user_boards = Board.query.filter_by(
        user_id=current_user.id,
        terminated_at=None
    ).all()

    # If no exact username matches, try partial username matches
    if not exact_matches:
        # Search for usernames containing the search term anywhere
        partial_matches = (
            User.query
                .filter(User.username.ilike(search_pattern),
                        User.terminated_at == None,
                        User.id != current_user.id)
                .all()
        )
        
        return render_template("search_results.html", 
                            users=partial_matches,
                            posts=matching_posts,
                            search_term=search_term,
                            search_type="partial",
                            current_user_boards=current_user_boards)
    
    return render_template("search_results.html", 
                         users=exact_matches,
                         posts=matching_posts,
                         search_term=search_term,
                         search_type="exact",
                         current_user_boards=current_user_boards)
