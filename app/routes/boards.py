from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Board, Pin, Post, FollowStream
from sqlalchemy.orm import joinedload
from sqlalchemy import and_
from datetime import datetime

boards_bp = Blueprint('boards', __name__)

@boards_bp.route('/boards')
@login_required
def list_boards():
    boards = Board.query.filter_by(user_id=current_user.id, terminated_at=None).all()
    return render_template('boards/list.html', boards=boards)

@boards_bp.route('/boards/<int:board_id>')
@login_required
def view_board(board_id):
    # Get the board without checking user_id to allow viewing other people's boards
    board = Board.query.filter_by(id=board_id, terminated_at=None).first_or_404()
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

    # Get current user's boards for repinning and streams for adding board
    current_user_boards = []
    current_user_streams = []
    
    if board.user_id != current_user.id:  # Only get boards if viewing someone else's board
        current_user_boards = Board.query.filter_by(
            user_id=current_user.id,
            terminated_at=None
        ).all()
        
        # Get current user's streams for adding board to stream
        current_user_streams = FollowStream.query.filter_by(
            user_id=current_user.id,
            terminated_at=None
        ).all()

    return render_template('boards/view.html', 
                         pins=pins_with_posts, 
                         board=board,
                         current_user_boards=current_user_boards,
                         current_user_streams=current_user_streams)


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

@boards_bp.route('/repin', methods=['POST'])
@login_required
def repin():
    post_id = request.form.get('post_id')
    board_id = request.form.get('board_id')
    source_pin_id = request.form.get('source_pin_id')

    if not all([post_id, board_id, source_pin_id]):
        flash("Missing required information for repinning.", "error")
        return redirect(url_for('dashboard.dashboard'))

    try:
        # Verify the board belongs to the current user
        board = Board.query.filter_by(
            id=board_id,
            user_id=current_user.id,
            terminated_at=None
        ).first()

        if not board:
            flash("Invalid board selected.", "error")
            return redirect(url_for('dashboard.dashboard'))

        # Check if the post is already pinned to this board
        existing_pin = Pin.query.filter_by(
            post_id=post_id,
            board_id=board_id,
            terminated_at=None
        ).first()

        if existing_pin:
            flash("This post is already pinned to the selected board.", "error")
            return redirect(url_for('dashboard.dashboard'))

        # Create new pin with reference to source pin
        new_pin = Pin(
            post_id=post_id,
            board_id=board_id,
            root_pin_id=source_pin_id,
            created_at=datetime.utcnow()
        )
        db.session.add(new_pin)
        db.session.commit()

        flash("Successfully repinned to your board!", "success")
        return redirect(url_for('boards.view_board', board_id=board_id))

    except Exception as e:
        db.session.rollback()
        print(f"Error repinning: {str(e)}")
        flash("An error occurred while repinning.", "error")
        return redirect(url_for('dashboard.dashboard'))
