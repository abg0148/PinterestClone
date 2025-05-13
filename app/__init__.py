from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from config import Config

# Initialize extensions globally (not yet bound to app)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Bind extensions to the app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Import models after app is created to avoid circular imports
    from app.models import User

    # Register the user loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter_by(id=user_id, terminated_at=None).first()

    # Import all blueprints
    from app.routes.auth import auth_bp
    from app.routes.profile import profile_bp
    from app.routes.boards import boards_bp
    from app.routes.posts import posts_bp
    from app.routes.social import social_bp
    from app.routes.friends import friends_bp
    from app.routes.follow_streams import follow_streams_bp
    from app.routes.dashboard import dashboard_bp

    # Register all blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(boards_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(social_bp)
    app.register_blueprint(friends_bp)
    app.register_blueprint(follow_streams_bp)
    app.register_blueprint(dashboard_bp)

    # Add no-cache headers for authenticated users
    @app.after_request
    def add_no_cache_headers(response):
        if current_user.is_authenticated:
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response

    # Register CLI commands
    from app.cli import init_app as init_cli_db
    from app.cli import init_cli as init_cli_commands
    init_cli_db(app)
    init_cli_commands(app)

    return app