from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Post, Pin, Board
from datetime import datetime
import uuid

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/posts/create', methods=['GET', 'POST'])
@login_required
def create_post():
    boards = Board.query.filter_by(user_id=current_user.id, terminated_at=None).all()

    if request.method == 'POST':
        tags_raw = request.form['tags'].strip()
        tags = ','.join(tag.strip() for tag in tags_raw.split() if ',' not in tag)

        image_url = request.form.get('image_url', '').strip() or None
        source_page = request.form.get('source_page', '').strip() or None
        image_blob = request.files.get('image_blob')
        board_id = request.form.get('board_id')

        if not tags or not board_id or not image_blob:
            flash("Tags, board, and image are required.", "error")
            return render_template('create_post.html', boards=boards)

        # Generate fallback image_url if not provided
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
            return redirect(url_for('dashboard.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash("Something went wrong while creating the post.", "error")
            print(e)

    return render_template('create_post.html', boards=boards)

from flask import send_file, abort
from io import BytesIO

@posts_bp.route('/media/<path:generated_id>')
def serve_generated_image(generated_id):
    internal_url = f"/media/{generated_id}"
    post = Post.query.filter_by(image_url=internal_url, terminated_at=None).first()

    if post and post.image_blob:
        return send_file(BytesIO(post.image_blob), mimetype='image/jpeg')
    else:
        abort(404)
