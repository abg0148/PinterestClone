from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Friend, User, FriendRequest, Post, Pin, Board
from datetime import datetime
from sqlalchemy import or_, and_

friends_bp = Blueprint('friends', __name__)

@friends_bp.route('/profile/search', methods=['GET', 'POST'])
@login_required
def search_user():
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

@friends_bp.route('/friends/request', methods=['POST'])
@login_required
def add_friend():
    from_id = current_user.id
    to_id = request.form.get("target_id")

    if from_id is None or to_id is None:
        flash("No Current user.", "error")
        return redirect(url_for('dashboard.dashboard'))
    
    try:
        to_id = int(to_id)
    except (ValueError, TypeError):
        flash("Invalid user ID.", "error")
        return redirect(url_for('dashboard.dashboard'))

    if from_id == to_id:
        flash("Cannot send friend request to self.", "error")
        return redirect(url_for('dashboard.dashboard'))
    
    if from_id != current_user.id:
        # Never trust the client for who is sending the request
        flash("from_id must match the logged‑in user", "error")
        return redirect(url_for('dashboard.dashboard'))
    
    # Check if target user exists and is active
    target = (
        User.query
            .filter(User.id == to_id, User.terminated_at == None)
            .first()
    )
    
    if not target:
        flash("User not found or is no longer active.", "error")
        return redirect(url_for('dashboard.dashboard'))

    # Check for existing active friendship
    existing_friendship = Friend.query.filter(
        or_(
            and_(Friend.user_id_1 == from_id, Friend.user_id_2 == to_id),
            and_(Friend.user_id_1 == to_id, Friend.user_id_2 == from_id)
        ),
        Friend.terminated_at == None
    ).first()

    if existing_friendship:
        flash("You are already friends with this user.", "error")
        return redirect(url_for('profile.view_profile', user_id=to_id))

    # Check for existing pending request
    already = (
        FriendRequest.query
            .filter(
                FriendRequest.sender_id == from_id,
                FriendRequest.receiver_id == to_id,
                FriendRequest.status == "pending",
                FriendRequest.terminated_at == None
            )
            .first()
    )
    
    if already:
        flash("Request already pending", "error")
        return redirect(url_for('profile.view_profile', user_id=to_id))
    
    # Check for existing request from target user
    reverse_request = (
        FriendRequest.query
            .filter(
                FriendRequest.sender_id == to_id,
                FriendRequest.receiver_id == from_id,
                FriendRequest.status == "pending",
                FriendRequest.terminated_at == None
            )
            .first()
    )
    
    if reverse_request:
        flash("This user has already sent you a friend request. Please respond to their request instead.", "error")
        return redirect(url_for('profile.view_profile', user_id=to_id))

    try:
        fr = FriendRequest(sender_id=from_id, receiver_id=to_id, status="pending")
        db.session.add(fr)
        db.session.commit()
    except Exception as e:
        print(f"Error sending friend request: {str(e)}")
        db.session.rollback()
        flash("Error sending friend request.", "error")
    
    return redirect(url_for('profile.view_profile', user_id=to_id))

@friends_bp.route('/friends/response', methods=['POST'])
@login_required
def friend_request_response():
    try:
        # Get form data
        sender_id = request.form.get("from_id")
        receiver_id = request.form.get("to_id")
        response = request.form.get("response")

        # Validate input data exists
        if not all([sender_id, receiver_id, response]):
            flash("Missing required data.", "error")
            return redirect(url_for('friends.list_request'))

        # Validate response type
        if response not in ['accepted', 'declined']:
            flash("Invalid response type.", "error")
            return redirect(url_for('friends.list_request'))

        # Convert IDs to integers
        try:
            sender_id = int(sender_id)
            receiver_id = int(receiver_id)
        except (ValueError, TypeError):
            flash("Invalid user IDs provided.", "error")
            return redirect(url_for('friends.list_request'))

        # Verify current user is the receiver
        if receiver_id != current_user.id:
            flash("You can only respond to your own friend requests.", "error")
            return redirect(url_for('friends.list_request'))

        # Verify both users still exist and are active
        sender = User.query.filter_by(id=sender_id, terminated_at=None).first()
        if not sender:
            flash("The user who sent this request is no longer active.", "error")
            return redirect(url_for('friends.list_request'))

        # Find the friend request and ensure it's still active
        friend_request = FriendRequest.query.filter_by(
            sender_id=sender_id,
            receiver_id=receiver_id,
            status="pending",
            terminated_at=None
        ).first()

        if not friend_request:
            flash("Friend request not found or already processed.", "error")
            return redirect(url_for('friends.list_request'))

        # Update the request status and mark as terminated
        friend_request.status = response
        friend_request.terminated_at = datetime.utcnow()

        if response == 'accepted':
            # Check if friendship already exists
            existing_friendship = Friend.query.filter(
                or_(
                    and_(Friend.user_id_1 == sender_id, Friend.user_id_2 == receiver_id),
                    and_(Friend.user_id_1 == receiver_id, Friend.user_id_2 == sender_id)
                ),
                Friend.terminated_at == None
            ).first()

            if not existing_friendship:
                # Always store the smaller ID in user_id_1 to maintain consistency
                user_id_1 = min(sender_id, receiver_id)
                user_id_2 = max(sender_id, receiver_id)
                friendship = Friend(user_id_1=user_id_1, user_id_2=user_id_2)
                db.session.add(friendship)

        try:
            db.session.commit()
            flash(
                "Friend request accepted!" if response == 'accepted' else "Friend request declined.",
                "success"
            )
        except Exception as e:
            print(f"Error saving changes: {str(e)}")
            db.session.rollback()
            flash("Error saving changes.", "error")

        return redirect(url_for('friends.list_request'))

    except Exception as e:
        print(f"Unexpected error in friend request response: {str(e)}")
        flash("An unexpected error occurred.", "error")
        return redirect(url_for('friends.list_request'))

@friends_bp.route('/friends/request_list', methods=['GET', 'POST'])
@login_required
def list_request():
    try:
        pending_requests = (
            FriendRequest.query
            .filter_by(receiver_id=current_user.id, status='pending')
            .join(User, FriendRequest.sender_id == User.id)
            .with_entities(
                User.username.label('username'),
                User.email.label('email'),
                FriendRequest.sender_id.label('from_id')
            )
            .all()
        )
        return render_template('friends/list.html', requests=pending_requests)
    except Exception as e:
        flash("An error occurred while loading friend requests.", "error")
        return redirect(url_for('dashboard.dashboard'))

@friends_bp.route('/friends', methods=['GET', 'POST'])
@login_required
def list_friends():
    # Get active friendships where either user is the current user
    friends = (
        Friend.query
            .filter(
                or_(Friend.user_id_1 == current_user.id,
                    Friend.user_id_2 == current_user.id),
                Friend.terminated_at == None  # Only active friendships
            )
            .all()
    )
    
    # Get the IDs of the other users in each friendship
    other_user_ids = [
        f.user_id_2 if f.user_id_1 == current_user.id else f.user_id_1
        for f in friends
    ]

    # Get active users from those IDs
    other_users = (
        User.query
            .filter(
                User.id.in_(other_user_ids),
                User.terminated_at == None  # Only active users
            )
            .all()
    )

    return render_template('friends/list_friends.html', friends=other_users)