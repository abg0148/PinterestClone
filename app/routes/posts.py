from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, abort
from flask_login import login_required, current_user
from app import db
from app.models import Post, Pin, Board
from datetime import datetime
import uuid
import requests
from io import BytesIO

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/posts/create', methods=['GET', 'POST'])
@login_required
def create_post():
    boards = Board.query.filter_by(user_id=current_user.id, terminated_at=None).all()
    
    # Get pre-selected board from query params
    pre_selected_board_id = request.args.get('board_id', type=int)
    pre_selected_board = None
    
    if pre_selected_board_id:
        pre_selected_board = Board.query.filter_by(
            id=pre_selected_board_id,
            user_id=current_user.id,
            terminated_at=None
        ).first()
    else:
        # If no board is pre-selected, default to Unorganized Ideas board
        pre_selected_board = Board.query.filter_by(
            user_id=current_user.id,
            board_name="Unorganized Ideas",
            terminated_at=None
        ).first()

    if request.method == 'POST':
        # Get form data
        tags_raw = request.form.get('tags', '').strip()
        board_id = request.form.get('board_id')
        image_url = request.form.get('image_url', '').strip()
        source_page = request.form.get('source_page', '').strip()
        image_file = request.files.get('image_blob')

        # Validate required fields
        if not tags_raw:
            flash("Tags are required.", "error")
            return render_template('create_post.html', boards=boards, pre_selected_board=pre_selected_board)
        
        if not board_id:
            flash("Please select a board.", "error")
            return render_template('create_post.html', boards=boards, pre_selected_board=pre_selected_board)

        # Process tags - split by comma and clean
        tags = ','.join(tag.strip() for tag in tags_raw.split(',') if tag.strip())
        
        if not tags:  # If no valid tags after processing
            flash("Please provide at least one valid tag.", "error")
            return render_template('create_post.html', boards=boards, pre_selected_board=pre_selected_board)

        # Validate board exists and belongs to user
        board = Board.query.filter_by(id=board_id, user_id=current_user.id, terminated_at=None).first()
        if not board:
            flash("Invalid board selected.", "error")
            return render_template('create_post.html', boards=boards, pre_selected_board=pre_selected_board)

        # Handle image source
        image_blob = None
        final_image_url = None

        # Check if we have either an image URL or an uploaded file
        if not image_url and not (image_file and image_file.filename):
            flash("Please either provide an image URL or upload an image file.", "error")
            return render_template('create_post.html', boards=boards, pre_selected_board=pre_selected_board)

        # If both are provided, prioritize the uploaded file
        if image_file and image_file.filename:
            image_blob = image_file.read()
            generated_id = f"generated-{uuid.uuid4()}"
            final_image_url = f"/media/{generated_id}"
        elif image_url:
            if not source_page:
                flash("Source page is required when using an image URL.", "error")
                return render_template('create_post.html', boards=boards, pre_selected_board=pre_selected_board)
            
            try:
                # Download the image
                response = requests.get(image_url)
                response.raise_for_status()  # Raises an HTTPError for bad responses
                image_blob = response.content
                final_image_url = image_url
            except Exception as e:
                flash("Error downloading image from URL. Please check the URL or try uploading the image directly.", "error")
                print(f"Error downloading image: {str(e)}")
                return render_template('create_post.html', boards=boards, pre_selected_board=pre_selected_board)

        try:
            # Create the Post
            new_post = Post(
                user_id=current_user.id,
                tags=tags,
                image_url=final_image_url,
                source_page=source_page if source_page else None,
                image_blob=image_blob,
                created_at=datetime.utcnow()
            )
            db.session.add(new_post)
            db.session.flush()  # To get post.id before committing

            # Create corresponding Pin
            new_pin = Pin(
                board_id=board_id,
                post_id=new_post.id,
                created_at=datetime.utcnow()
            )
            db.session.add(new_pin)

            db.session.commit()
            flash("Post created and pinned successfully!", "success")
            return redirect(url_for('boards.view_board', board_id=board_id))
        except Exception as e:
            db.session.rollback()
            flash("Something went wrong while creating the post.", "error")
            print(f"Error creating post: {str(e)}")
            return render_template('create_post.html', boards=boards, pre_selected_board=pre_selected_board)

    return render_template('create_post.html', boards=boards, pre_selected_board=pre_selected_board)

@posts_bp.route('/media/<path:generated_id>')
def serve_generated_image(generated_id):
    internal_url = f"/media/{generated_id}"
    post = Post.query.filter_by(image_url=internal_url, terminated_at=None).first()

    if post and post.image_blob:
        return send_file(BytesIO(post.image_blob), mimetype='image/jpeg')
    else:
        abort(404)

# Remove or comment out the view_post route since we're moving it to boards blueprint
# @posts_bp.route('/posts/<int:post_id>')
# @login_required
# def view_post(post_id):
#     post = Post.query.filter_by(id=post_id, terminated_at=None).first_or_404()
#     pin = Pin.query.filter_by(post_id=post_id, terminated_at=None).first_or_404()
#     board = Board.query.get_or_404(pin.board_id)
#     
#     # Get current user's boards for repinning
#     current_user_boards = []
#     if board.user_id != current_user.id:
#         current_user_boards = Board.query.filter_by(
#             user_id=current_user.id,
#             terminated_at=None
#         ).all()
#     
#     return render_template('posts/view.html',
#                          post=post,
#                          pin=pin,
#                          board=board,
#                          current_user_boards=current_user_boards)
