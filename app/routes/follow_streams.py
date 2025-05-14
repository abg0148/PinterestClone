from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import FollowStream, FollowStreamBoard, Board, Pin, Post
from datetime import datetime
from sqlalchemy import and_

follow_streams_bp = Blueprint('follow_streams', __name__)

@follow_streams_bp.route('/follow-streams')
@login_required
def list_streams():
    """List all follow streams owned by the current user."""
    streams = (
        FollowStream.query
        .filter_by(user_id=current_user.id, terminated_at=None)
        .all()
    )
    return render_template('follow_streams/list.html', streams=streams)

@follow_streams_bp.route('/follow-streams/create', methods=['GET', 'POST'])
@login_required
def create_stream():
    """Create a new follow stream."""
    if request.method == 'POST':
        stream_name = request.form.get('stream_name', '').strip()
        
        if not stream_name:
            flash("Stream name is required.", "error")
            return redirect(url_for('follow_streams.create_stream'))
        
        # Check if stream name already exists for this user
        existing = (
            FollowStream.query
            .filter_by(
                user_id=current_user.id,
                stream_name=stream_name,
                terminated_at=None
            )
            .first()
        )
        
        if existing:
            flash("You already have a stream with this name.", "error")
            return redirect(url_for('follow_streams.create_stream'))
        
        try:
            stream = FollowStream(
                user_id=current_user.id,
                stream_name=stream_name
            )
            db.session.add(stream)
            db.session.commit()
            flash("Follow stream created successfully!", "success")
            return redirect(url_for('follow_streams.view_stream', stream_id=stream.id))
        except Exception as e:
            db.session.rollback()
            flash("Error creating follow stream.", "error")
            print(f"Error creating follow stream: {str(e)}")
            return redirect(url_for('follow_streams.create_stream'))
    
    return render_template('follow_streams/create.html')

@follow_streams_bp.route('/follow-streams/<int:stream_id>')
@login_required
def view_stream(stream_id):
    """View a follow stream and its pins."""
    stream = FollowStream.query.get_or_404(stream_id)
    
    # Ensure user owns this stream
    if stream.user_id != current_user.id:
        flash("Access denied.", "error")
        return redirect(url_for('follow_streams.list_streams'))
    
    # Get all boards in this stream
    stream_boards = (
        FollowStreamBoard.query
        .filter_by(stream_id=stream_id, deleted_at=None)
        .all()
    )
    
    board_ids = [sb.board_id for sb in stream_boards]
    
    # Get all pins from these boards
    pins = (
        db.session.query(Pin, Post, Board)
        .join(Post, and_(Pin.post_id == Post.id, Post.terminated_at == None))
        .join(Board, and_(Pin.board_id == Board.id, Board.terminated_at == None))
        .filter(
            Pin.board_id.in_(board_ids),
            Pin.terminated_at == None
        )
        .order_by(Post.created_at.desc())
        .all()
    )
    
    return render_template('follow_streams/view.html', 
                         stream=stream, 
                         stream_boards=stream_boards,
                         pins=pins)

@follow_streams_bp.route('/follow-streams/<int:stream_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_stream(stream_id):
    """Edit a follow stream's name and remove boards."""
    stream = FollowStream.query.get_or_404(stream_id)
    
    # Ensure user owns this stream
    if stream.user_id != current_user.id:
        flash("Access denied.", "error")
        return redirect(url_for('follow_streams.list_streams'))
    
    if request.method == 'POST':
        if 'stream_name' in request.form:
            # Handle stream name update
            new_name = request.form['stream_name'].strip()
            if new_name:
                stream.stream_name = new_name
                try:
                    db.session.commit()
                    flash("Stream name updated successfully.", "success")
                except Exception as e:
                    db.session.rollback()
                    flash("Error updating stream name.", "error")
                    print(f"Error updating stream name: {str(e)}")
            else:
                flash("Stream name cannot be empty.", "error")
        
        elif 'board_id' in request.form and request.form.get('action') == 'remove':
            # Handle board removal
            board_id = request.form.get('board_id', type=int)
            try:
                stream_board = (
                    FollowStreamBoard.query
                    .filter_by(
                        stream_id=stream_id,
                        board_id=board_id,
                        deleted_at=None
                    )
                    .first()
                )
                
                if stream_board:
                    stream_board.deleted_at = datetime.utcnow()
                    db.session.commit()
                    flash("Board removed from stream.", "success")
                else:
                    flash("Board not found in stream.", "error")
                
            except Exception as e:
                db.session.rollback()
                flash("Error removing board from stream.", "error")
                print(f"Error removing board: {str(e)}")
        
        return redirect(url_for('follow_streams.edit_stream', stream_id=stream_id))
    
    # Get current boards in stream
    current_boards = (
        FollowStreamBoard.query
        .filter_by(stream_id=stream_id, deleted_at=None)
        .all()
    )
    
    return render_template('follow_streams/edit.html',
                         stream=stream,
                         current_boards=current_boards)

@follow_streams_bp.route('/board/<int:board_id>/add-to-stream', methods=['POST'])
@login_required
def add_board_to_stream(board_id):
    """Add a board to a stream from the board view."""
    stream_id = request.form.get('stream_id', type=int)
    
    if not stream_id:
        flash("Please select a stream.", "error")
        return redirect(url_for('boards.view_board', board_id=board_id))
    
    # Verify stream exists and belongs to user
    stream = FollowStream.query.filter_by(
        id=stream_id,
        user_id=current_user.id,
        terminated_at=None
    ).first_or_404()
    
    # Verify board exists
    board = Board.query.filter_by(id=board_id, terminated_at=None).first_or_404()
    
    try:
        # Check if already in stream (and not deleted)
        existing = (
            FollowStreamBoard.query
            .filter_by(
                stream_id=stream_id,
                board_id=board_id,
                deleted_at=None
            )
            .first()
        )
        
        if existing:
            flash("This board is already in the selected stream.", "info")
        else:
            # Check if it was previously deleted and reactivate it
            deleted = (
                FollowStreamBoard.query
                .filter_by(
                    stream_id=stream_id,
                    board_id=board_id
                )
                .filter(FollowStreamBoard.deleted_at != None)
                .first()
            )
            
            if deleted:
                deleted.deleted_at = None
                flash("Board added back to stream.", "success")
            else:
                # Create new association
                stream_board = FollowStreamBoard(
                    stream_id=stream_id,
                    board_id=board_id
                )
                db.session.add(stream_board)
                flash("Board added to stream successfully!", "success")
            
            db.session.commit()
            
    except Exception as e:
        db.session.rollback()
        flash("Error adding board to stream.", "error")
        print(f"Error adding board to stream: {str(e)}")
    
    return redirect(url_for('boards.view_board', board_id=board_id)) 