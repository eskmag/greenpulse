"""
JWT Authentication API endpoints
"""
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required, 
    get_jwt_identity, 
    get_jwt,
    current_user
)
from app.models import User, db

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Store revoked tokens (in production, use Redis)
revoked_tokens = set()


@bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return JWT tokens"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password required'}), 400
        
        user = User.query.filter_by(email=data['email'], is_active=True).first()
        
        if user and user.check_password(data['password']):
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Create tokens with additional claims
            access_token = create_access_token(
                identity=user,
                additional_claims=user.get_jwt_claims()
            )
            refresh_token = create_refresh_token(identity=user)
            
            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token using refresh token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 404
        
        new_token = create_access_token(
            identity=user,
            additional_claims=user.get_jwt_claims()
        )
        
        return jsonify({
            'access_token': new_token,
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user by revoking token"""
    try:
        jti = get_jwt()['jti']  # JWT ID
        revoked_tokens.add(jti)
        
        return jsonify({'message': 'Successfully logged out'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """Get current user profile"""
    try:
        return jsonify({
            'user': current_user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify if token is valid"""
    try:
        claims = get_jwt()
        
        return jsonify({
            'valid': True,
            'user_id': get_jwt_identity(),
            'role': claims.get('role'),
            'company_id': claims.get('company_id'),
            'exp': claims.get('exp')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
