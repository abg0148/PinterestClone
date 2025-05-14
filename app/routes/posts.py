from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, abort
from flask_login import login_required, current_user
from app import db
from app.models import Post, Pin, Board
from datetime import datetime
import uuid
from io import BytesIO
import requests
from werkzeug.datastructures import FileStorage

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/posts/create', methods=['GET', 'POST'])
@login_required
def create_post():
    boards = Board.query.filter_by(user_id=current_user.id, terminated_at=None).all()

    if request.method == 'POST':
        # Get form data
        tags_raw = request.form.get('tags', '').strip()
        board_id = request.form.get('board_id')
        image_url = request.form.get('image_url', '').strip() or None
        source_page = request.form.get('source_page', '').strip() or None
        image_blob = request.files.get('image_blob')

        # If image_blob not present, attempt to fetch from image_url
        if not image_blob and image_url:
            try:
                response = requests.get(image_url)
                response.raise_for_status()
                filename = image_url.split("/")[-1] or "downloaded_image"
                image_blob = FileStorage(
                    stream=BytesIO(response.content),
                    filename=filename,
                    content_type=response.headers.get('Content-Type', 'application/octet-stream')
                )
            except Exception as e:
                flash(f"Failed to download image from URL, please upload the image")
                return render_template('create_post.html', boards=boards)

        # Validate required fields
        if not tags_raw:
            flash("Tags are required.", "error")
            return render_template('create_post.html', boards=boards)
        
        if not board_id:
            flash("Please select a board.", "error")
            return render_template('create_post.html', boards=boards)

        if not image_blob:
            flash("Please upload an image or provide a valid image URL.", "error")
            return render_template('create_post.html', boards=boards)

        # Process tags - split by comma and clean
        tags = ','.join(tag.strip() for tag in tags_raw.split(',') if tag.strip())
        if not tags:
            flash("Please provide at least one valid tag.", "error")
            return render_template('create_post.html', boards=boards)

        # Validate board exists and belongs to user
        board = Board.query.filter_by(id=board_id, user_id=current_user.id, terminated_at=None).first()
        if not board:
            flash("Invalid board selected.", "error")
            return render_template('create_post.html', boards=boards)

        # Validate image file
        if not image_blob.filename:
            flash("Invalid image file.", "error")
            return render_template('create_post.html', boards=boards)

        # Generate image URL if not provided
        if not image_url:
            generated_id = f"generated-{uuid.uuid4()}"
            final_image_url = f"/media/{generated_id}"
        else:
            final_image_url = image_url

        try:
            # Create the Post
            new_post = Post(
                user_id=current_user.id,
                tags=tags,
                image_url=final_image_url,
                source_page=source_page,
                image_blob=image_blob.read(),
                created_at=datetime.utcnow()
            )
            db.session.add(new_post)
            db.session.flush()

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
            return render_template('create_post.html', boards=boards)

    return render_template('create_post.html', boards=boards)

@posts_bp.route('/media/<path:generated_id>')
def serve_generated_image(generated_id):
    internal_url = f"/media/{generated_id}"
    post = Post.query.filter_by(image_url=internal_url, terminated_at=None).first()

    if post and post.image_blob:
        return send_file(BytesIO(post.image_blob), mimetype='image/jpeg')
    else:
        abort(404)

@posts_bp.route('/posts/delete', methods=['GET', 'POST'])
@login_required
def delete_post():
    post_ids = request.json.get('post_ids', [])
    post_ids = [int(pid) for pid in post_ids if str(pid).isdigit()]

    if not post_ids:
        return {"error": "No valid post IDs provided"}, 400

    try:
        soft_delete_posts(post_ids)
        return {"message": "Posts soft deleted successfully."}, 200
    except Exception as e:
        return {"error": str(e)}, 500

def soft_delete_posts(post_ids):
    if not post_ids:
        return
    
    posts = Post.query.filter(Post.id.in_(post_ids), Post.terminated_at.is_(None)).all()
    pins = Pin.query.filter(Pin.post_id.in_(post_ids), Pin.terminated_at.is_(None)).all()

    try:
        for post in posts:
            post.terminated_at = datetime.utcnow()
        for pin in pins:
            pin.terminated_at = datetime.utcnow()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error during deletion of posts: {str(e)}")
        raise