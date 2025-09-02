#!/usr/bin/env python3
"""
GreenPulse Flask Web Application
Main entry point for the web application with database integration
"""
import os
import enum
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from logging.handlers import RotatingFileHandler

# Initialize Flask app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://localhost/greenpulse_dev')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define models
class UserRole(enum.Enum):
    ADMIN = "admin"
    COMPANY_ADMIN = "company_admin"
    USER = "user"
    VIEWER = "viewer"

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    org_number = db.Column(db.String(20), unique=True, nullable=False)
    industry_sector = db.Column(db.String(100))
    employee_count = db.Column(db.Integer)
    headquarters_location = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', back_populates='company', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'org_number': self.org_number,
            'industry_sector': self.industry_sector,
            'employee_count': self.employee_count,
            'headquarters_location': self.headquarters_location,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.USER)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    company = db.relationship('Company', back_populates='users')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role.value,
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }

# API Routes
@app.route('/')
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

@app.route('/health')
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

# Company Management APIs
@app.route('/api/companies', methods=['GET'])
def list_companies():
    """List all companies (admin view)"""
    try:
        companies = Company.query.all()
        return jsonify({
            'companies': [company.to_dict() for company in companies],
            'total': len(companies)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/companies/<int:company_id>', methods=['GET'])
def get_company(company_id):
    """Get specific company details"""
    try:
        company = Company.query.get_or_404(company_id)
        users = User.query.filter_by(company_id=company.id).all()
        
        return jsonify({
            'company': {
                'id': company.id,
                'name': company.name,
                'slug': company.slug,
                'org_number': company.org_number,
                'industry_sector': company.industry_sector,
                'employee_count': company.employee_count,
                'headquarters_location': company.headquarters_location,
                'subscription_plan': company.subscription_plan,
                'is_active': company.is_active,
                'created_at': company.created_at.isoformat() if company.created_at else None
            },
            'users': [
                {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role.value,
                    'is_active': user.is_active,
                    'last_login': user.last_login.isoformat() if user.last_login else None
                } for user in users
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/companies', methods=['POST'])
def create_company():
    """Create new company"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('name'):
            return jsonify({'error': 'Company name is required'}), 400
        
        # Create slug from name
        slug = data['name'].lower().replace(' ', '-').replace('&', 'and')
        
        # Check if company name or slug already exists
        existing = Company.query.filter(
            (Company.name == data['name']) | (Company.slug == slug)
        ).first()
        
        if existing:
            return jsonify({'error': 'Company name already exists'}), 409
        
        company = Company(
            name=data['name'],
            slug=slug,
            org_number=data.get('org_number'),
            industry_sector=data.get('industry_sector'),
            employee_count=data.get('employee_count'),
            headquarters_location=data.get('headquarters_location'),
            subscription_plan=data.get('subscription_plan', 'basic')
        )
        
        db.session.add(company)
        db.session.commit()
        
        return jsonify({
            'message': 'Company created successfully',
            'company': {
                'id': company.id,
                'name': company.name,
                'slug': company.slug,
                'industry_sector': company.industry_sector,
                'created_at': company.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# User Management APIs
@app.route('/api/users', methods=['GET'])
def list_users():
    """List all users (admin view)"""
    try:
        users = User.query.all()
        return jsonify({
            'users': [
                {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role.value,
                    'company_id': user.company_id,
                    'company_name': user.company.name if user.company else None,
                    'is_active': user.is_active,
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'created_at': user.created_at.isoformat() if user.created_at else None
                } for user in users
            ],
            'total': len(users)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name', 'company_id']
        for field in required_fields:
            if not data or not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if email already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 409
        
        # Check if company exists
        company = Company.query.get(data['company_id'])
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Determine role
        role_str = data.get('role', 'user').upper()
        try:
            role = UserRole[role_str]
        except KeyError:
            return jsonify({'error': f'Invalid role: {role_str}'}), 400
        
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
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role.value,
                'company_id': user.company_id,
                'created_at': user.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Authentication placeholder
@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login (basic implementation)"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if user and user.check_password(data['password']):
            # Update last login
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            
            return jsonify({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role.value,
                    'company_id': user.company_id,
                    'company_name': user.company.name
                },
                'note': 'JWT tokens will be implemented in next phase'
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Demo data endpoint
@app.route('/api/demo/reset', methods=['POST'])
def reset_demo_data():
    """Reset and recreate demo data"""
    try:
        # This is for development only - would not exist in production
        from add_demo_data import add_demo_companies
        
        # Clear existing data (be careful!)
        User.query.delete()
        Company.query.delete()
        db.session.commit()
        
        # Add demo companies again
        with app.app_context():
            from add_demo_data import add_demo_companies
            add_demo_companies()
        
        return jsonify({'message': 'Demo data reset successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables exist
    app.run(debug=False, port=5002, host='127.0.0.1')