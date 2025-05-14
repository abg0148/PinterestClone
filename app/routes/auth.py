from werkzeug.security import generate_password_hash
from app import db
from sqlalchemy.exc import IntegrityError
from flask import Blueprint, render_template, request, redirect, url_for, flash, get_flashed_messages
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from app.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    return render_template('index.html')

@auth_bp.route('/auth/signup', methods=['GET', 'POST'])
def signup():
    # If user is logged in, log them out first
    if current_user.is_authenticated:
        logout_user()
        
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']

        if not username or not email or not password:
            flash("All fields are required.", "error")
        else:
            try:
                # Create user
                new_user = User(
                    username=username,
                    email=email,
                    password_hash=generate_password_hash(password)
                )
                db.session.add(new_user)
                db.session.commit()

                # Create default board
                try:
                    new_user.create_default_board()
                except Exception as e:
                    flash("Account created but default board creation failed. Please try creating a board manually.", "warning")
                    print(f"Default board creation error: {str(e)}")

                login_user(new_user)
                return redirect(url_for('dashboard.dashboard'))
            except IntegrityError:
                db.session.rollback()
                flash("Username or email already taken.", "error")

    return render_template('signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in, redirect to dashboard
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.dashboard'))
        return redirect(url_for('auth.index'))

    if request.method == 'POST':
        identifier = request.form['identifier'].strip()
        password = request.form['password']

        # Try to find user by either username or email
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier.lower()),
            User.terminated_at.is_(None)
        ).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash("Invalid username/email or password.", "error")
            return redirect(url_for('auth.index'))

@auth_bp.route('/logout')
@login_required
def logout():
    # Clear any existing flash messages
    _ = get_flashed_messages()
    
    # Log out the user
    logout_user()
    
    # Add logout message
    flash("You have been logged out.", "success")
    return redirect(url_for('auth.index'))

# Create default boards for existing users
def create_default_boards_for_existing_users():
    """Utility function to create default boards for all existing users."""
    users = User.query.filter_by(terminated_at=None).all()
    for user in users:
        try:
            user.create_default_board()
        except Exception as e:
            print(f"Error creating default board for user {user.username}: {str(e)}")

