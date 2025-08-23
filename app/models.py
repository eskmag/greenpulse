"""
Database models for GreenPulse
"""
import enum
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


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
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import enum

# Import db from extensions
from app.extensions import db

class UserRole(enum.Enum):
    """User roles for role-based access control"""
    ADMIN = "admin"
    COMPANY_ADMIN = "company_admin"
    USER = "user"
    VIEWER = "viewer"

class Company(db.Model):
    """Company/Tenant model for multi-tenant architecture"""
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    slug = db.Column(db.String(80), nullable=False, unique=True, index=True)
    
    # Company details
    org_number = db.Column(db.String(20), unique=True)  # Norwegian org number
    industry_sector = db.Column(db.String(80))
    employee_count = db.Column(db.Integer)
    headquarters_location = db.Column(db.String(120))
    
    # Subscription/plan information
    subscription_plan = db.Column(db.String(50), default='basic')
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    users = db.relationship('User', backref='company', lazy='dynamic')
    data_uploads = db.relationship('DataUpload', backref='company', lazy='dynamic')
    reports = db.relationship('Report', backref='company', lazy='dynamic')
    
    def __repr__(self):
        return f'<Company {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'org_number': self.org_number,
            'industry_sector': self.industry_sector,
            'employee_count': self.employee_count,
            'headquarters_location': self.headquarters_location,
            'subscription_plan': self.subscription_plan,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class User(UserMixin, db.Model):
    """User model with multi-tenant support"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # User details
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.USER)
    
    # Company association (tenant)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    
    # Account status
    is_active = db.Column(db.Boolean, default=True)
    email_confirmed = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def has_role(self, role):
        """Check if user has specific role"""
        return self.role == role
    
    def is_company_admin(self):
        """Check if user is company admin"""
        return self.role in [UserRole.ADMIN, UserRole.COMPANY_ADMIN]
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'role': self.role.value,
            'company_id': self.company_id,
            'is_active': self.is_active,
            'email_confirmed': self.email_confirmed,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'

class DataUpload(db.Model):
    """Track data uploads for each company"""
    __tablename__ = 'data_uploads'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # File details
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)
    file_type = db.Column(db.String(50))  # csv, xlsx, etc.
    
    # Processing status
    status = db.Column(db.String(50), default='uploaded')  # uploaded, processing, completed, failed
    rows_processed = db.Column(db.Integer, default=0)
    errors_count = db.Column(db.Integer, default=0)
    processing_log = db.Column(db.Text)
    
    # Data categorization
    data_category = db.Column(db.String(80))  # emissions, energy, efficiency, etc.
    reporting_period = db.Column(db.String(20))  # year or date range
    
    # Timestamps
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    processed_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref='uploads')
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'status': self.status,
            'rows_processed': self.rows_processed,
            'errors_count': self.errors_count,
            'data_category': self.data_category,
            'reporting_period': self.reporting_period,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'uploaded_by': self.user.full_name if self.user else None
        }

class Report(db.Model):
    """Generated reports for companies"""
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Report details
    title = db.Column(db.String(200), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)  # csrd, esg, efficiency, etc.
    file_path = db.Column(db.String(500))
    file_format = db.Column(db.String(20))  # pdf, xlsx, etc.
    
    # Report metadata
    reporting_period_start = db.Column(db.Date)
    reporting_period_end = db.Column(db.Date)
    parameters = db.Column(db.JSON)  # Store report parameters/filters
    
    # Generation status
    status = db.Column(db.String(50), default='generating')  # generating, completed, failed
    generation_log = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref='generated_reports')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'report_type': self.report_type,
            'file_format': self.file_format,
            'status': self.status,
            'reporting_period_start': self.reporting_period_start.isoformat() if self.reporting_period_start else None,
            'reporting_period_end': self.reporting_period_end.isoformat() if self.reporting_period_end else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'generated_by': self.user.full_name if self.user else None
        }

class AuditLog(db.Model):
    """Audit log for tracking user actions"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Action details
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50))  # user, company, data, report, etc.
    resource_id = db.Column(db.Integer)
    details = db.Column(db.JSON)
    
    # Request metadata
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    
    # Timestamp
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = db.relationship('User', backref='audit_logs')
    company = db.relationship('Company', backref='audit_logs')
    
    def to_dict(self):
        return {
            'id': self.id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'user': self.user.full_name if self.user else 'System'
        }
