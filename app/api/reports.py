"""
Reports API endpoints
"""
from flask import Blueprint, jsonify

bp = Blueprint('reports', __name__, url_prefix='/api/reports')


@bp.route('/esg', methods=['GET'])
def esg_report():
    """Generate ESG report"""
    return jsonify({
        'message': 'ESG reporting feature coming soon',
        'status': 'in_development'
    })


@bp.route('/emissions', methods=['GET'])
def emissions_report():
    """Generate emissions report"""
    return jsonify({
        'message': 'Emissions reporting feature coming soon',
        'status': 'in_development'
    })
