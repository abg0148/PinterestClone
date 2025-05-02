from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Friend, User, FriendRequest
from datetime import datetime
import uuid

friends_bp = Blueprint('friends', __name__)

@friends_bp.route('/profile/search', methods=['GET'])
@login_required
def search_user():
    username = request.args.get("username", type=str)
    if not username:
        flash("Bad Request.", "error")
        return

    user = (
        User.query
            .filter(User.username == username,
                    User.terminated_at == None)
            .first_or_404()
    )

    return redirect(url_for('dashboard.dashboard'))

@friends_bp.route('/friends/request', methods=['POST'])
@login_required
def add_friend():
    data = request.get_json(force=True, silent=True) or {}
    from_id = data.get("from_id")
    to_id   = data.get("to_id")

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
            .filter((FriendRequest.from_id == from_id,
                     FriendRequest.to_id   == to_id,
                     FriendRequest.status   == "pending")
            )
            .first()
    )
    if already:
        flash("Request already pending", "error")
    
    fr = FriendRequest(from_id=from_id, to_id=to_id, status="pending")
    db.session.add(fr)
    db.session.commit()

    flash("Post created and pinned successfully!", "success")
    return redirect(url_for('dashboard.dashboard'))
    