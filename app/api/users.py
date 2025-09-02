"""
Users API endpoints with JWT protection
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt, current_user
from app.models import User, Company, UserRole, db

bp = Blueprint('users', __name__, url_prefix='/api/users')


def require_admin_or_company_admin():
    """Check if user has admin or company_admin role"""
    claims = get_jwt()
    user_role = claims.get('role')
    return user_role in ['admin', 'company_admin']


def can_access_user(target_user_id):
    """Check if current user can access target user data"""
    claims = get_jwt()
    user_role = claims.get('role')
    current_company_id = claims.get('company_id')
    
    # Admins can access any user
    if user_role == 'admin':
        return True
    
    # Company admins can access users in their company
    if user_role == 'company_admin':
        target_user = User.query.get(target_user_id)
        return target_user and target_user.company_id == current_company_id
    
    # Users can only access their own data
    return int(target_user_id) == int(current_user.id)


@bp.route('/', methods=['GET'])
@jwt_required()
def list_users():
    """List users (filtered by access level)"""
    try:
        claims = get_jwt()
        user_role = claims.get('role')
        current_company_id = claims.get('company_id')
        
        if user_role == 'admin':
            # Admins see all users
            users = User.query.all()
        elif user_role == 'company_admin':
            # Company admins see users in their company
            users = User.query.filter_by(company_id=current_company_id).all()
        else:
            # Regular users see only themselves
            users = [current_user]
        
        return jsonify({
            'users': [user.to_dict() for user in users],
            'total': len(users)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['POST'])
@jwt_required()
def create_user():
    """Create a new user (admin or company admin only)"""
    try:
        if not require_admin_or_company_admin():
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name', 'company_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 409
        
        # Validate company exists
        company = Company.query.get(data['company_id'])
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Company admins can only create users in their own company
        claims = get_jwt()
        if claims.get('role') == 'company_admin':
            if data['company_id'] != claims.get('company_id'):
                return jsonify({'error': 'Cannot create user for different company'}), 403
        
        # Validate role
        role = UserRole.USER  # default
        if 'role' in data:
            try:
                role = UserRole(data['role'])
                # Company admins cannot create admin users
                if claims.get('role') == 'company_admin' and role == UserRole.ADMIN:
                    return jsonify({'error': 'Cannot create admin users'}), 403
            except ValueError:
                return jsonify({'error': 'Invalid role'}), 400
        
        # Create new user
        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=role,
            company_id=data['company_id']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get user by ID (with access control)"""
    try:
        if not can_access_user(user_id):
            return jsonify({'error': 'Access denied'}), 403
            
        user = User.query.get_or_404(user_id)
        return jsonify({'user': user.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 404
