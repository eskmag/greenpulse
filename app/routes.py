"""
Main application routes
"""
from flask import Blueprint, jsonify
from datetime import datetime, timezone
from app.models import Company, User

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    return jsonify({
        'message': 'GreenPulse API is running!',
        'version': '1.0.0',
        'status': 'healthy',
        'database': 'checking...',
        'api_endpoints': {
            'Companies': '/api/companies',
            'Users': '/api/users', 
            'Authentication': '/api/auth',
            'Health': '/health'
        }
    })


@bp.route('/health')
def health():
    try:
        # Test database connection
        company_count = Company.query.count()
        user_count = User.query.count()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'statistics': {
                'companies': company_count,
                'users': user_count
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500
