from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Board, Pin, Post, FollowStream, Comment, Like, FollowStreamBoard
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
    """View a board and its pins."""
    board = Board.query.get_or_404(board_id)
    
    # Get all active pins for this board
    pins = (
        db.session.query(Pin, Post)
        .join(Post)
        .filter(
            Pin.board_id == board_id,
            Pin.terminated_at == None,
            Post.terminated_at == None
        )
        .order_by(Post.created_at.desc())
        .all()
    )

    # If viewing someone else's board, get current user's follow streams
    streams = None
    if board.user_id != current_user.id:
        streams = (
            FollowStream.query
            .filter_by(user_id=current_user.id, terminated_at=None)
            .order_by(FollowStream.stream_name)
            .all()
        )
    
    return render_template('boards/view.html', 
                         board=board, 
                         pins=pins,
                         streams=streams,
                         Like=Like)

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

@boards_bp.route('/boards/delete/<int:board_id>', methods=['POST'])
@login_required
def delete_board(board_id):
    board = Board.query.filter_by(id=board_id, user_id=current_user.id, terminated_at=None).first_or_404()
    
    try:
        # Get all active pins in this board
        pins = Pin.query.filter_by(board_id=board_id, terminated_at=None).all()
        
        # Delete each pin properly using our pin.delete() method
        for pin in pins:
            pin.delete()
        
        # Soft delete the board
        board.terminated_at = datetime.utcnow()
        
        # Mark all follow stream associations as deleted
        FollowStreamBoard.query.filter_by(
            board_id=board_id,
            deleted_at=None
        ).update({"deleted_at": datetime.utcnow()})
        
        db.session.commit()
        flash("Board deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting the board.", "error")
        print(f"Error deleting board: {str(e)}")
    
    return redirect(url_for('boards.list_boards'))
