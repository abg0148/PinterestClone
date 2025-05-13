from flask_login import current_user

from .auth import auth_bp
from .dashboard import dashboard_bp
from .profile import profile_bp
from .boards import boards_bp
from .posts import posts_bp
from .friends import friends_bp
from .social import social_bp
from .search import search_bp

def init_routes(app):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(boards_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(friends_bp)
    app.register_blueprint(social_bp)
    app.register_blueprint(search_bp)

    @app.after_request
    def add_no_cache_headers(response):
        if current_user.is_authenticated:
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response
