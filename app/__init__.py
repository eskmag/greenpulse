"""
GreenPulse Flask Application Factory
"""
import os
from flask import Flask, jsonify
from flask_login import LoginManager
from flask_jwt_extended import get_jwt, get_jwt_identity

# Import extensions
from app.extensions import db, migrate, jwt


def configure_jwt(app):
    """Configure JWT settings and callbacks"""
    
    # Ensure JWT_SECRET_KEY is set
    if not app.config.get('JWT_SECRET_KEY'):
        app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']
    
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        """Convert user object to identity for JWT"""
        return str(user.id)  # Convert to string as required by JWT
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        """Load user from JWT identity"""
        from app.models import User
        identity = jwt_data["sub"]
        # Convert back to int for database query
        return User.query.filter_by(id=int(identity)).one_or_none()
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Handle expired tokens"""
        return jsonify({
            'error': 'token_expired',
            'message': 'The token has expired'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """Handle invalid tokens"""
        return jsonify({
            'error': 'invalid_token',
            'message': 'Invalid token'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """Handle missing tokens"""
        return jsonify({
            'error': 'missing_token',
            'message': 'Authorization token required'
        }), 401


def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    from config import config_map
    app.config.from_object(config_map.get(config_name, config_map['default']))
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Configure JWT
    configure_jwt(app)
    
    # Register blueprints
    from app.api import companies, users, auth, reports
    app.register_blueprint(companies.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(reports.bp)
    
    # Register main routes
    from app import routes
    app.register_blueprint(routes.bp)
    
    return app
    
    # Register main routes
    from app import routes
    app.register_blueprint(routes.bp)
    
    return app
