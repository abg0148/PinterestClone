from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Board, FollowStream

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    boards = Board.query.filter_by(user_id=current_user.id, terminated_at=None).all()
    streams = FollowStream.query.filter_by(user_id=current_user.id, terminated_at=None).all()
    return render_template('dashboard.html', user=current_user, boards=boards, streams=streams)

