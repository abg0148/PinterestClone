from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from io import BytesIO
from app import db
from app.models import User

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

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

        return redirect(url_for('profile.profile'))

    return render_template('edit_profile.html', user=current_user)

@profile_bp.route('/profile/picture/<int:user_id>')
@login_required
def profile_picture(user_id):
    user = User.query.get_or_404(user_id)
    if user.picture:
        return send_file(BytesIO(user.picture), mimetype='image/jpeg')
    else:
        # Fallback to a default placeholder image from /static/
        return redirect(url_for('static', filename='placeholder.jpg'))
