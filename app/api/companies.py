"""
Companies API endpoints with JWT protection
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt, current_user
from app.models import Company, db

bp = Blueprint('companies', __name__, url_prefix='/api/companies')


def require_admin():
    """Check if user has admin role"""
    claims = get_jwt()
    return claims.get('role') == 'admin'


@bp.route('/', methods=['GET'])
@jwt_required()
def list_companies():
    """List companies (filtered by access level)"""
    try:
        claims = get_jwt()
        user_role = claims.get('role')
        
        if user_role == 'admin':
            # Admins see all companies
            companies = Company.query.all()
        else:
            # Other users see only their company
            current_company_id = claims.get('company_id')
            companies = Company.query.filter_by(id=current_company_id).all()
        
        return jsonify({
            'companies': [company.to_dict() for company in companies],
            'total': len(companies)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/', methods=['POST'])
@jwt_required()
def create_company():
    """Create a new company (admin only)"""
    try:
        if not require_admin():
            return jsonify({'error': 'Admin access required'}), 403
            
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'org_number']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if company already exists
        existing_company = Company.query.filter_by(org_number=data['org_number']).first()
        if existing_company:
            return jsonify({'error': 'Company with this organization number already exists'}), 409
        
        # Create new company
        company = Company(
            name=data['name'],
            org_number=data['org_number'],
            industry_sector=data.get('industry_sector'),
            employee_count=data.get('employee_count'),
            headquarters_location=data.get('headquarters_location')
        )
        
        db.session.add(company)
        db.session.commit()
        
        return jsonify({
            'message': 'Company created successfully',
            'company': company.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:company_id>', methods=['GET'])
def get_company(company_id):
    """Get company by ID"""
    try:
        company = Company.query.get_or_404(company_id)
        return jsonify({'company': company.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@bp.route('/<int:company_id>', methods=['PUT'])
def update_company(company_id):
    """Update company information"""
    try:
        company = Company.query.get_or_404(company_id)
        data = request.get_json()
        
        # Update fields if provided
        if 'name' in data:
            company.name = data['name']
        if 'industry_sector' in data:
            company.industry_sector = data['industry_sector']
        if 'employee_count' in data:
            company.employee_count = data['employee_count']
        if 'headquarters_location' in data:
            company.headquarters_location = data['headquarters_location']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Company updated successfully',
            'company': company.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:company_id>', methods=['DELETE'])
def delete_company(company_id):
    """Delete company"""
    try:
        company = Company.query.get_or_404(company_id)
        
        # Check if company has users
        if company.users.count() > 0:
            return jsonify({'error': 'Cannot delete company with existing users'}), 409
        
        db.session.delete(company)
        db.session.commit()
        
        return jsonify({'message': 'Company deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
