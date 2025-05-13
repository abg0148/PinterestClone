from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Friend, User, FriendRequest
from datetime import datetime
from sqlalchemy import or_, and_

friends_bp = Blueprint('friends', __name__)

@friends_bp.route('/profile/search', methods=['GET', 'POST'])
@login_required
def search_user():
    username = request.form.get("identifier", type=str)
    if not username:
        flash("Bad Request.", "error")
        return

    user = (
        User.query
            .filter(User.username == username,
                    User.terminated_at == None,
                    User.id != current_user.id)
            .first()
    )

    if not user:
        flash("No such user", "error")
        return redirect(url_for('dashboard.dashboard'))

    return render_template("user_profile.html", user=user)

@friends_bp.route('/friends/request', methods=['POST'])
@login_required
def add_friend():
    from_id = current_user.id
    to_id   = request.form.get("target_id")

    if from_id is None or to_id is None:
        flash("No Current user.", "error")
    if from_id == to_id:
        flash("Cannot send friend request to self.", "error")
    if from_id != current_user.id:
        # Never trust the client for who is sending the request
        flash("from_id must match the logged‑in user", "error")
    
    target = (
        User.query
            .filter(User.id == to_id, User.terminated_at == None)  # noqa: E711
            .first_or_404()
    )

    already = (
        FriendRequest.query
            .filter(and_(FriendRequest.sender_id == from_id,
                     FriendRequest.receiver_id   == to_id,
                     FriendRequest.status   == "pending")
            )
            .first()
    )
    if already:
        flash("Request already pending", "error")
    
    fr = FriendRequest(sender_id=from_id, receiver_id=to_id, status="pending")
    db.session.add(fr)
    db.session.commit()

    flash("Sent friend request successfully!", "success")
    return redirect(url_for('dashboard.dashboard'))

@friends_bp.route('/friends/response', methods=['POST'])
@login_required
def friend_request_response():
    sender_id = request.form.get("from_id")
    receiver_id = request.form.get("to_id")
    response = request.form.get("response")

    if sender_id is None or receiver_id is None:
        flash("User id is null/User does not exist.", "error")
    if sender_id == receiver_id:
        flash("Sender id is same as receiver id.", "error")

    friend_request = (
        FriendRequest.query
            .filter(and_(FriendRequest.sender_id == sender_id,
                     FriendRequest.receiver_id   == receiver_id,
                     FriendRequest.status   == "pending")
            )
            .first()
    )

    friend_request.status = response
    friend_request.terminated_at = datetime.utcnow()

    if response == 'accepted':
        friendship = Friend(user_id_1=sender_id, user_id_2=receiver_id)
        db.session.add(friendship)

    db.session.commit()

    if response == 'accepted':
        flash("Friend Added successfully!", "success")
    else:
        flash("Request Declined Successfully", "success")

    return redirect(url_for('dashboard.dashboard'))

@friends_bp.route('/friends/request_list', methods=['GET', 'POST'])
@login_required
def list_request():
    pending_requests = (
        FriendRequest.query
        .filter_by(receiver_id=current_user.id, status='pending')
        .join(User, FriendRequest.sender_id == User.id)
        .with_entities(User.username.label('username'), 
               User.email.label('email'), 
               FriendRequest.id.label('id'), 
               FriendRequest.sender_id.label('from_id'))
        .all()
    )

    return render_template('friends/list.html', requests=pending_requests)

@friends_bp.route('/friends', methods=['GET', 'POST'])
@login_required
def list_friends():
    friends = (
        Friend.query
            .filter(or_(Friend.user_id_1 == current_user.id,
                        Friend.user_id_2   == current_user.id)
                        
            )
            .all()
    )
    other_user_ids = [
    f.user_id_2 if f.user_id_1 == current_user.id else f.user_id_1
    for f in friends
    ]

    other_users = User.query.filter(User.id.in_(other_user_ids)).all()

    return render_template('friends/list_friends.html', friends=other_users)