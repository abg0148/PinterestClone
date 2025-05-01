from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# Initialize extensions globally (not yet bound to app)
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Bind extensions to the app
    db.init_app(app)
    login_manager.init_app(app)

    # Import models after app is created to avoid circular imports
    from app.models import User

    # Register the user loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter_by(id=user_id, terminated_at=None).first()

    # Register routes
    from app.routes import init_routes
    init_routes(app)

    # Register CLI commands
    from app.cli import init_app as init_cli
    init_cli(app)

    return app