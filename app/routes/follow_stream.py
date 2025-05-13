from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Board, FollowStreamBoard, FollowStream
from sqlalchemy.orm import joinedload
from sqlalchemy import and_

boards_bp = Blueprint('boards', __name__)

@boards_bp.route('/streams')
@login_required
def list_streams():
    streams = FollowStream.query.filter_by(user_id=current_user.id, terminated_at=None).all()
    # return render_template('boards/list.html', boards=boards)
    return streams

@boards_bp.route('/stream/<int:stream_id>')
@login_required
def view_stream(stream_id):
    stream = FollowStream.query.filter_by(id=stream_id, user_id=current_user.id, terminated_at=None).first_or_404()
    stream_with_boards = (
        db.session.query(FollowStream, FollowStreamBoard, Board)
        .join(FollowStream, and_(FollowStreamBoard.stream_id == FollowStream.id, FollowStream.terminated_at == None))
        .join(Board, and_(Board.id == FollowStreamBoard.board_id, Board.terminated_at == None))
        .filter(
            FollowStream.id == stream.id,
            FollowStreamBoard.stream_id == stream.id,
            FollowStream.terminated_at == None
        )
        .order_by(FollowStream.created_at.desc())
        .all()
    )

    # return render_template('boards/view.html', pins=pins_with_posts, board=board)
    return stream_with_boards


@boards_bp.route('/stream/create', methods=['GET', 'POST'])
@login_required
def create_stream():
    if request.method == 'POST':
        name = request.form['name'].strip()

        if not name:
            flash("Stream name is required.", "error")
        else:
            new_stream = FollowStream(
                user_id=current_user.id,
                stream_name=name
            )
            db.session.add(new_stream)
            try:
                db.session.commit()
                # return redirect(url_for('dashboard.dashboard'))
            except:
                db.session.rollback()
                flash("Stream name must be unique.", "error")

    # return render_template('boards/create.html')
    return new_stream

@boards_bp.route('/streams/<int:stream_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_board(stream_id):
    stream = FollowStream.query.filter_by(id=stream_id, user_id=current_user.id, terminated_at=None).first_or_404()

    if request.method == 'POST':
        new_stream = FollowStream(
                board_id=request.form['board_id'].strip(),
                stream_id=stream.id
            )
        db.session.add(new_stream)

        try:
            db.session.commit()
            flash("Stream updated successfully.", "success")
            # return redirect(url_for('dashboard.dashboard'))
        except:
            db.session.rollback()
            flash("Board can only be added to stream once.", "error")

    # return render_template('boards/edit.html', board=board)
    return new_stream