from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Board, Pin, Post
from sqlalchemy.orm import joinedload
from sqlalchemy import and_

boards_bp = Blueprint('boards', __name__)

@boards_bp.route('/boards')
@login_required
def list_boards():
    boards = Board.query.filter_by(user_id=current_user.id, terminated_at=None).all()
    return render_template('boards/list.html', boards=boards)

@boards_bp.route('/boards/<int:board_id>')
@login_required
def view_board(board_id):
    board = Board.query.filter_by(id=board_id, user_id=current_user.id, terminated_at=None).first_or_404()
    pins_with_posts = (
        db.session.query(Pin, Post)
        .join(Post, and_(Pin.post_id == Post.id, Post.terminated_at == None))
        .filter(
            Pin.board_id == board_id,
            Pin.terminated_at == None
        )
        .order_by(Pin.created_at.desc())
        .all()
    )

    return render_template('boards/view.html', pins=pins_with_posts, board=board)


@boards_bp.route('/boards/create', methods=['GET', 'POST'])
@login_required
def create_board():
    if request.method == 'POST':
        name = request.form['name'].strip()
        description = request.form['description'].strip()
        allow_comments = request.form.get('allow_comments') == 'on'

        if not name:
            flash("Board name is required.", "error")
        else:
            new_board = Board(
                user_id=current_user.id,
                board_name=name,
                description=description,
                allow_public_comments=allow_comments
            )
            db.session.add(new_board)
            try:
                db.session.commit()
                return redirect(url_for('dashboard.dashboard'))
            except:
                db.session.rollback()
                flash("Board name must be unique.", "error")

    return render_template('boards/create.html')

@boards_bp.route('/boards/<int:board_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_board(board_id):
    board = Board.query.filter_by(id=board_id, user_id=current_user.id, terminated_at=None).first_or_404()

    if request.method == 'POST':
        board.board_name = request.form['name'].strip()
        board.description = request.form['description'].strip()
        board.allow_public_comments = request.form.get('allow_comments') == 'on'

        try:
            db.session.commit()
            flash("Board updated successfully.", "success")
            return redirect(url_for('dashboard.dashboard'))
        except:
            db.session.rollback()
            flash("Board name must be unique.", "error")

    return render_template('boards/edit.html', board=board)
