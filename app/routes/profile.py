from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, abort
from flask_login import login_required, current_user
from io import BytesIO
from app import db
from app.models import User, Friend, FriendRequest, Board
from sqlalchemy import or_, and_

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile/<int:user_id>/view')
@login_required
def view_profile(user_id):
    user = User.query.filter_by(id=user_id, terminated_at=None).first_or_404()
    
    # Get user's friends
    friend_records = Friend.query.filter(
        or_(
            and_(Friend.user_id_1 == user.id, Friend.terminated_at == None),
            and_(Friend.user_id_2 == user.id, Friend.terminated_at == None)
        )
    ).all()
    
    # Get the friend user objects
    friend_ids = [
        f.user_id_2 if f.user_id_1 == user.id else f.user_id_1
        for f in friend_records
    ]
    friends = User.query.filter(
        User.id.in_(friend_ids),
        User.terminated_at == None
    ).all()
    
    # Get user's boards
    boards = Board.query.filter_by(user_id=user.id, terminated_at=None).all()
    
    # Don't check friendship status for own profile
    if user.id == current_user.id:
        return render_template('profile.html', user=user, friendship_status=None, friends=friends, boards=boards)

    # Check if they are already friends
    friendship = Friend.query.filter(
        or_(
            and_(Friend.user_id_1 == current_user.id, Friend.user_id_2 == user.id),
            and_(Friend.user_id_1 == user.id, Friend.user_id_2 == current_user.id)
        ),
        Friend.terminated_at == None
    ).first()

    if friendship:
        friendship_status = 'friends'
    else:
        # Check for pending friend requests
        pending_request = FriendRequest.query.filter(
            or_(
                and_(
                    FriendRequest.sender_id == current_user.id,
                    FriendRequest.receiver_id == user.id,
                    FriendRequest.status == 'pending'
                ),
                and_(
                    FriendRequest.sender_id == user.id,
                    FriendRequest.receiver_id == current_user.id,
                    FriendRequest.status == 'pending'
                )
            )
        ).first()

        if pending_request:
            if pending_request.sender_id == current_user.id:
                friendship_status = 'pending_sent'
            else:
                friendship_status = 'pending_received'
        else:
            friendship_status = 'not_friends'

    return render_template('profile.html', user=user, friendship_status=friendship_status, friends=friends, boards=boards)

@profile_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        full_name = request.form['full_name'].strip()
        bio = request.form['bio'].strip()
        picture = request.files.get('picture')

        current_user.full_name = full_name
        current_user.bio = bio

        if picture and picture.filename:
            current_user.picture = picture.read()

        try:
            db.session.commit()
            flash("Profile updated successfully!", "success")
        except Exception:
            db.session.rollback()
            flash("Something went wrong. Please try again.", "error")

        return redirect(url_for('profile.view_profile', user_id=current_user.id))

    return render_template('edit_profile.html', user=current_user)

@profile_bp.route('/profile/<int:user_id>/picture')
def profile_picture(user_id):
    user = User.query.filter_by(id=user_id, terminated_at=None).first_or_404()
    if user.picture:
        return send_file(BytesIO(user.picture), mimetype='image/jpeg')
    else:
        # Fallback to a default placeholder image from /static/
        return redirect(url_for('static', filename='placeholder.jpg'))

@profile_bp.route('/profile/<int:user_id>/friends')
@login_required
def view_friends(user_id):
    user = User.query.filter_by(id=user_id, terminated_at=None).first_or_404()
    
    # Get user's friends
    friend_records = Friend.query.filter(
        or_(
            and_(Friend.user_id_1 == user.id, Friend.terminated_at == None),
            and_(Friend.user_id_2 == user.id, Friend.terminated_at == None)
        )
    ).all()
    
    # Get the friend user objects
    friend_ids = [
        f.user_id_2 if f.user_id_1 == user.id else f.user_id_1
        for f in friend_records
    ]
    friends = User.query.filter(
        User.id.in_(friend_ids),
        User.terminated_at == None
    ).all()
    
    return render_template('profile_friends.html', user=user, friends=friends)

# Redirect old profile URL to user's own profile view
@profile_bp.route('/profile')
@login_required
def profile_redirect():
    return redirect(url_for('profile.view_profile', user_id=current_user.id))
