---
name: airfinder
description: Reproduce the complete Airfinder travel booking system from scratch — flight search, booking, admin portal, staff management.
---

# Airfinder — Full System Rebuild

## What This Builds
Full-stack travel booking platform. Flask backend, SQLite DB, JWT auth, RBAC, vanilla JS frontend. Mock flight data (Africa-focused). True Cost Engine, AI search, multi-city booking, admin CRM.

## Client Quick Start
```
# Prerequisites: Python 3.10+, pip
cd airfinder
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
python backend/app.py
```
Open http://localhost:5000

**Admin login:** http://localhost:5000/admin/login.html  
Email: `admin@airfinder.com` Password: `Admin@2024!`

**Customer:** register at http://localhost:5000/auth/register.html

## Create Directory Structure
```powershell
mkdir airfinder
cd airfinder
mkdir backend\models, backend\middleware, backend\routes, backend\services, backend\tests
mkdir frontend\css, frontend\js, frontend\auth, frontend\account, frontend\admin
New-Item backend\__init__.py, backend\models\__init__.py, backend\middleware\__init__.py, backend\routes\__init__.py, backend\services\__init__.py, backend\tests\__init__.py -ItemType File
```

---

## FILE: .env
```
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=airfinder-super-secret-key-change-in-prod-2024
JWT_SECRET=airfinder-jwt-secret-key-change-in-prod-2024
DATABASE_URL=sqlite:///airfinder.db
PORT=5000
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=noreply@airfinder.com
MAIL_PASSWORD=your-mail-password-here
MAIL_DEFAULT_SENDER=Airfinder <noreply@airfinder.com>
DEFAULT_MARKUP_PERCENT=8
DEFAULT_SERVICE_FEE_USD=15
DEFAULT_COMMISSION_PERCENT=3
SUPER_ADMIN_EMAIL=admin@airfinder.com
SUPER_ADMIN_PASSWORD=Admin@2024!
```

## FILE: requirements.txt
```
flask==3.0.3
flask-cors==4.0.1
flask-sqlalchemy==3.1.1
flask-mail==0.10.0
flask-limiter==3.8.0
PyJWT>=2.10.1,<3.0.0
bcrypt==4.1.3
python-dotenv==1.0.1
pytest==8.2.2
pytest-flask==1.3.0
```

## FILE: .gitignore
```
__pycache__/
*.pyc
*.pyo
.env
*.db
*.sqlite3
.venv/
venv/
env/
dist/
build/
*.egg-info/
.DS_Store
Thumbs.db
node_modules/
```

## FILE: CLAUDE.md
```
# Airfinder — Project Notes

## Stack
- Backend: Python + Flask (port 5000)
- DB: SQLite (airfinder.db) via SQLAlchemy
- Auth: JWT + bcrypt
- Frontend: Vanilla HTML/CSS/JS in /frontend/

## Run
python backend/app.py

## Default Credentials
- Super Admin: admin@airfinder.com / Admin@2024!
- Staff accounts: created by admin, emailed temp password, must change on first login

## Key APIs
- POST /api/auth/register — customer signup
- POST /api/auth/login — customer login
- POST /api/staff/auth/login — staff login
- POST /api/staff/auth/change-password — force change (works even with must_change_password=True)
- GET /api/flights/search — flight search
- POST /api/flights/search/ai — NL query search
- POST /api/flights/search/multicity — multi-leg search
- POST /api/bookings — create booking (auth required)
- POST /api/bookings/multicity — multi-city booking (auth required)
- GET /api/flights/status?flight=XX&date=YYYY-MM-DD — flight status/tracking (deterministic mock)
- GET /api/admin/dashboard — admin stats
- GET /api/admin/staff — staff list
- POST /api/admin/staff — create staff
- GET /api/admin/finance/summary — revenue data

## Roles
super_admin > admin > agent > finance > customer

## Revenue Config (.env)
DEFAULT_MARKUP_PERCENT=8
DEFAULT_SERVICE_FEE_USD=15
DEFAULT_COMMISSION_PERCENT=3

## Frontend Pages
- / — search homepage
- /results.html — search results
- /booking.html — booking flow
- /confirmation.html — booking confirmed
- /multicity.html — multi-city results + booking
- /flight-status.html — flight tracking page
- /auth/login.html, /auth/register.html, /auth/forgot-password.html
- /account/dashboard.html, /account/bookings.html, /account/profile.html
- /admin/* — staff portal

## Airport Database (mock_flights.py)
191 airports with lat/lon. Germany: FRA MUC DUS BER HAM STR CGN NUE HAJ LEJ DRS BSL FKB.
Nigeria: LOS ABV PHC KAN ENU. Full coverage: Africa, Middle East, Europe, Americas, Asia, Oceania.
Haversine-based flight durations. AIRPORT_CARRIERS whitelist restricts airlines per regional airport.

## Airline Routing
50 airlines, 6 regions, longhaul bool. _eligible_airlines() builds pool per route.
AIRPORT_CARRIERS whitelist: PHC/KAN/ENU = Nigerian+African carriers only.
German secondaries (STR/CGN etc) = Lufthansa/Eurowings/LCC only.
```

---

## FILE: backend/app.py
```python
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os
from backend.config import Config
from backend.models.database import init_db
from backend.extensions import limiter

def create_app():
    app = Flask(__name__, static_folder='../frontend', static_url_path='')
    app.config.from_object(Config)
    CORS(app, resources={r'/api/*': {'origins': '*'}})
    limiter.init_app(app)
    init_db(app)
    from backend.routes import auth_customer, auth_staff, flights, bookings, admin, staff_mgmt
    app.register_blueprint(auth_customer.bp)
    app.register_blueprint(auth_staff.bp)
    app.register_blueprint(flights.bp)
    app.register_blueprint(bookings.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(staff_mgmt.bp)
    @app.route('/')
    def index(): return send_from_directory(app.static_folder, 'index.html')
    @app.route('/auth/<path:filename>')
    def auth_pages(filename): return send_from_directory(os.path.join(app.static_folder, 'auth'), filename)
    @app.route('/account/<path:filename>')
    def account_pages(filename): return send_from_directory(os.path.join(app.static_folder, 'account'), filename)
    @app.route('/admin/<path:filename>')
    def admin_pages(filename): return send_from_directory(os.path.join(app.static_folder, 'admin'), filename)
    @app.errorhandler(404)
    def not_found(e): return jsonify({'error': 'Not found'}), 404
    @app.errorhandler(500)
    def server_error(e): return jsonify({'error': 'Internal server error'}), 500
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=Config.PORT, debug=True)
```

## FILE: backend/config.py
```python
import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    JWT_SECRET = os.getenv('JWT_SECRET', 'dev-jwt-secret')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///airfinder.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'Airfinder <noreply@airfinder.com>')
    MARKUP_PERCENT = float(os.getenv('DEFAULT_MARKUP_PERCENT', 8))
    SERVICE_FEE_USD = float(os.getenv('DEFAULT_SERVICE_FEE_USD', 15))
    COMMISSION_PERCENT = float(os.getenv('DEFAULT_COMMISSION_PERCENT', 3))
    SUPER_ADMIN_EMAIL = os.getenv('SUPER_ADMIN_EMAIL', 'admin@airfinder.com')
    SUPER_ADMIN_PASSWORD = os.getenv('SUPER_ADMIN_PASSWORD', 'Admin@2024!')
    PORT = int(os.getenv('PORT', 5000))
```

## FILE: backend/extensions.py
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
limiter = Limiter(key_func=get_remote_address, default_limits=[], storage_uri="memory://")
```

## FILE: backend/models/database.py
```python
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, inspect as sa_inspect
db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    with app.app_context():
        from backend.models import user, staff, booking
        db.create_all()
        _migrate_existing(app)
        _seed_super_admin(app)

def _migrate_existing(app):
    inspector = sa_inspect(db.engine)
    if 'bookings' not in inspector.get_table_names(): return
    existing = {c['name'] for c in inspector.get_columns('bookings')}
    additions = []
    if 'group_reference' not in existing:
        additions.append('ALTER TABLE bookings ADD COLUMN group_reference VARCHAR(20)')
    if 'is_multicity' not in existing:
        additions.append('ALTER TABLE bookings ADD COLUMN is_multicity BOOLEAN DEFAULT 0')
    if additions:
        with db.engine.connect() as conn:
            for stmt in additions: conn.execute(text(stmt))
            conn.commit()

def _seed_super_admin(app):
    from backend.models.staff import Staff, StaffRole
    from backend.config import Config
    import bcrypt
    existing = Staff.query.filter_by(email=Config.SUPER_ADMIN_EMAIL).first()
    if existing: return
    hashed = bcrypt.hashpw(Config.SUPER_ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt())
    super_admin = Staff(email=Config.SUPER_ADMIN_EMAIL, password_hash=hashed.decode('utf-8'),
        first_name='Super', last_name='Admin', role=StaffRole.SUPER_ADMIN,
        must_change_password=False, is_active=True)
    db.session.add(super_admin)
    db.session.commit()
```

## FILE: backend/models/user.py
```python
import uuid
from datetime import datetime
from backend.models.database import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(30))
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(255))
    reset_token = db.Column(db.String(255))
    reset_token_expiry = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    bookings = db.relationship('Booking', backref='customer', lazy=True)
    def to_dict(self):
        return {'id': self.id, 'email': self.email, 'first_name': self.first_name,
            'last_name': self.last_name, 'phone': self.phone, 'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat()}
```

## FILE: backend/models/staff.py
```python
import uuid, enum
from datetime import datetime
from backend.models.database import db

class StaffRole(enum.Enum):
    SUPER_ADMIN = 'super_admin'
    ADMIN = 'admin'
    AGENT = 'agent'
    FINANCE = 'finance'

class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum(StaffRole), nullable=False, default=StaffRole.AGENT)
    must_change_password = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.String(36), db.ForeignKey('staff.id'), nullable=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    def to_dict(self):
        return {'id': self.id, 'email': self.email, 'first_name': self.first_name,
            'last_name': self.last_name, 'role': self.role.value,
            'must_change_password': self.must_change_password, 'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat()}

ROLE_HIERARCHY = {StaffRole.SUPER_ADMIN: 4, StaffRole.ADMIN: 3, StaffRole.AGENT: 2, StaffRole.FINANCE: 1}

def can_manage(actor_role: StaffRole, target_role: StaffRole) -> bool:
    return ROLE_HIERARCHY.get(actor_role, 0) > ROLE_HIERARCHY.get(target_role, 0)
```

## FILE: backend/models/booking.py
```python
import uuid, enum
from datetime import datetime
from backend.models.database import db

class BookingStatus(enum.Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    reference = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    flight_id = db.Column(db.String(100), nullable=False)
    origin = db.Column(db.String(10), nullable=False)
    destination = db.Column(db.String(10), nullable=False)
    departure_date = db.Column(db.String(20), nullable=False)
    airline = db.Column(db.String(100), nullable=False)
    flight_number = db.Column(db.String(20))
    cabin_class = db.Column(db.String(20), default='economy')
    passengers_json = db.Column(db.Text, nullable=False)
    passenger_count = db.Column(db.Integer, default=1)
    base_fare_usd = db.Column(db.Float, nullable=False)
    markup_usd = db.Column(db.Float, default=0)
    service_fee_usd = db.Column(db.Float, default=0)
    baggage_fee_usd = db.Column(db.Float, default=0)
    seat_fee_usd = db.Column(db.Float, default=0)
    total_usd = db.Column(db.Float, nullable=False)
    commission_usd = db.Column(db.Float, default=0)
    status = db.Column(db.Enum(BookingStatus), default=BookingStatus.PENDING)
    notes = db.Column(db.Text)
    agent_id = db.Column(db.String(36), db.ForeignKey('staff.id'), nullable=True)
    group_reference = db.Column(db.String(20), nullable=True, index=True)
    is_multicity = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    def to_dict(self):
        import json
        return {'id': self.id, 'reference': self.reference, 'user_id': self.user_id,
            'flight_id': self.flight_id, 'origin': self.origin, 'destination': self.destination,
            'departure_date': self.departure_date, 'airline': self.airline,
            'flight_number': self.flight_number, 'cabin_class': self.cabin_class,
            'passengers': json.loads(self.passengers_json), 'passenger_count': self.passenger_count,
            'pricing': {'base_fare': self.base_fare_usd, 'markup': self.markup_usd,
                'service_fee': self.service_fee_usd, 'baggage_fee': self.baggage_fee_usd,
                'seat_fee': self.seat_fee_usd, 'total': self.total_usd, 'commission': self.commission_usd},
            'status': self.status.value, 'notes': self.notes,
            'group_reference': self.group_reference, 'is_multicity': self.is_multicity or False,
            'created_at': self.created_at.isoformat()}

def generate_reference():
    import random, string
    return 'AF' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
```

## FILE: backend/middleware/jwt_guard.py
```python
import jwt
from functools import wraps
from flask import request, jsonify, current_app, g
from backend.models.user import User
from backend.models.staff import Staff

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _extract_token()
        if not token: return jsonify({'error': 'Authorization token required'}), 401
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=['HS256'])
            g.user_id = payload['user_id']
            g.role = payload['role']
            g.must_change_password = payload.get('must_change_password', False)
        except jwt.ExpiredSignatureError: return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError: return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

def staff_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _extract_token()
        if not token: return jsonify({'error': 'Authorization token required'}), 401
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=['HS256'])
            role = payload.get('role', '')
            if role not in ('super_admin', 'admin', 'agent', 'finance'):
                return jsonify({'error': 'Staff access required'}), 403
            g.user_id = payload['user_id']
            g.role = role
            g.must_change_password = payload.get('must_change_password', False)
            if g.must_change_password:
                return jsonify({'error': 'Password change required', 'must_change_password': True}), 403
        except jwt.ExpiredSignatureError: return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError: return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

def _extract_token():
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '): return auth_header[7:]
    return None
```

## FILE: backend/middleware/role_guard.py
```python
from functools import wraps
from flask import jsonify, g
from backend.middleware.jwt_guard import staff_required

def require_role(*allowed_roles):
    def decorator(f):
        @wraps(f)
        @staff_required
        def decorated(*args, **kwargs):
            if g.role not in allowed_roles:
                return jsonify({'error': f'Access denied. Required roles: {", ".join(allowed_roles)}'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
```

## FILE: backend/routes/auth_customer.py
```python
import jwt
import bcrypt
import uuid
import secrets
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app, g
from backend.models.database import db
from backend.models.user import User
from backend.middleware.jwt_guard import jwt_required
from backend.services.email_service import send_welcome_email, send_password_reset_email
from backend.extensions import limiter

bp = Blueprint('auth_customer', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
@limiter.limit("10 per hour")
def register():
    data = request.get_json()
    required = ['email', 'password', 'first_name', 'last_name']
    if not all(data.get(f) for f in required):
        return jsonify({'error': 'All fields required: email, password, first_name, last_name'}), 400
    if User.query.filter_by(email=data['email'].lower()).first():
        return jsonify({'error': 'Email already registered'}), 409
    if len(data['password']) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    hashed = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    verification_token = secrets.token_urlsafe(32)
    user = User(
        email=data['email'].lower(),
        password_hash=hashed.decode('utf-8'),
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone=data.get('phone'),
        verification_token=verification_token,
        is_verified=True,
    )
    db.session.add(user)
    db.session.commit()
    send_welcome_email(user.email, user.first_name)
    token = _generate_token(user.id, 'customer')
    return jsonify({'message': 'Account created successfully', 'token': token, 'user': user.to_dict()}), 201

@bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    data = request.get_json()
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    user = User.query.filter_by(email=data['email'].lower()).first()
    if not user or not bcrypt.checkpw(data['password'].encode('utf-8'), user.password_hash.encode('utf-8')):
        return jsonify({'error': 'Invalid credentials'}), 401
    if not user.is_active:
        return jsonify({'error': 'Account deactivated. Contact support.'}), 403
    token = _generate_token(user.id, 'customer')
    return jsonify({'token': token, 'user': user.to_dict()})

@bp.route('/forgot-password', methods=['POST'])
@limiter.limit("5 per hour")
def forgot_password():
    data = request.get_json()
    email = data.get('email', '').lower()
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'If that email exists, a reset link was sent.'})
    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=15)
    db.session.commit()
    base_url = request.host_url.rstrip('/')
    reset_link = f"{base_url}/auth/reset-password.html?token={token}"
    send_password_reset_email(user.email, user.first_name, reset_link)
    return jsonify({'message': 'If that email exists, a reset link was sent.'})

@bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('password')
    if not token or not new_password:
        return jsonify({'error': 'Token and new password required'}), 400
    if len(new_password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    user = User.query.filter_by(reset_token=token).first()
    if not user:
        return jsonify({'error': 'Invalid or expired token'}), 400
    if user.reset_token_expiry < datetime.utcnow():
        return jsonify({'error': 'Reset link has expired. Request a new one.'}), 400
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    user.password_hash = hashed.decode('utf-8')
    user.reset_token = None
    user.reset_token_expiry = None
    db.session.commit()
    return jsonify({'message': 'Password reset successfully. You can now log in.'})

@bp.route('/me', methods=['GET'])
@jwt_required
def me():
    user = User.query.get(g.user_id)
    if not user: return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict())

def _generate_token(user_id: str, role: str, must_change_password=False) -> str:
    payload = {
        'user_id': user_id, 'role': role,
        'must_change_password': must_change_password,
        'exp': datetime.utcnow() + timedelta(hours=24),
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET'], algorithm='HS256')
```

## FILE: backend/routes/auth_staff.py
```python
import jwt
import bcrypt
import secrets
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app, g
from backend.models.database import db
from backend.models.staff import Staff, StaffRole
from backend.middleware.jwt_guard import staff_required
from backend.extensions import limiter

bp = Blueprint('auth_staff', __name__, url_prefix='/api/staff/auth')

@bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def staff_login():
    data = request.get_json()
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    staff = Staff.query.filter_by(email=data['email'].lower()).first()
    if not staff or not bcrypt.checkpw(data['password'].encode('utf-8'), staff.password_hash.encode('utf-8')):
        return jsonify({'error': 'Invalid credentials'}), 401
    if not staff.is_active:
        return jsonify({'error': 'Account deactivated. Contact your administrator.'}), 403
    staff.last_login = datetime.utcnow()
    db.session.commit()
    token = _generate_staff_token(staff)
    return jsonify({'token': token, 'staff': staff.to_dict(), 'must_change_password': staff.must_change_password})

@bp.route('/change-password', methods=['POST'])
def change_password():
    """Force-change temporary password — works even when must_change_password=True"""
    token = _extract_token()
    if not token: return jsonify({'error': 'Authorization token required'}), 401
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=['HS256'])
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    staff = Staff.query.get(payload['user_id'])
    if not staff: return jsonify({'error': 'Staff not found'}), 404
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    if not current_password or not new_password:
        return jsonify({'error': 'current_password and new_password required'}), 400
    if not bcrypt.checkpw(current_password.encode('utf-8'), staff.password_hash.encode('utf-8')):
        return jsonify({'error': 'Current password is incorrect'}), 400
    if len(new_password) < 8:
        return jsonify({'error': 'New password must be at least 8 characters'}), 400
    if current_password == new_password:
        return jsonify({'error': 'New password must differ from temporary password'}), 400
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    staff.password_hash = hashed.decode('utf-8')
    staff.must_change_password = False
    db.session.commit()
    new_token = _generate_staff_token(staff)
    return jsonify({'message': 'Password changed successfully', 'token': new_token, 'staff': staff.to_dict()})

@bp.route('/me', methods=['GET'])
@staff_required
def me():
    staff = Staff.query.get(g.user_id)
    if not staff: return jsonify({'error': 'Staff not found'}), 404
    return jsonify(staff.to_dict())

def _generate_staff_token(staff: Staff) -> str:
    payload = {
        'user_id': staff.id, 'role': staff.role.value,
        'must_change_password': staff.must_change_password,
        'exp': datetime.utcnow() + timedelta(hours=12),
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET'], algorithm='HS256')

def _extract_token():
    auth = request.headers.get('Authorization', '')
    return auth[7:] if auth.startswith('Bearer ') else None
```

## FILE: backend/routes/flights.py
```python
from flask import Blueprint, request, jsonify
from backend.services.mock_flights import search_flights, get_featured_routes, get_airports
from backend.services.ai_search import parse_natural_language
from backend.services.pricing import calculate_total, BAGGAGE_FEES, SEAT_FEES

bp = Blueprint('flights', __name__, url_prefix='/api/flights')

@bp.route('/search', methods=['GET'])
def search():
    origin = request.args.get('origin', '').upper()
    destination = request.args.get('destination', '').upper()
    departure_date = request.args.get('departure_date')
    passengers = int(request.args.get('passengers', 1))
    cabin = request.args.get('cabin', 'economy')
    return_date = request.args.get('return_date')
    if not origin or not destination or not departure_date:
        return jsonify({'error': 'origin, destination, and departure_date are required'}), 400
    passengers = max(1, min(passengers, 9))
    results = search_flights(origin, destination, departure_date, passengers, cabin, return_date)
    budget = request.args.get('budget_max')
    if budget:
        try: results = [f for f in results if f['pricing']['total'] <= float(budget)]
        except (ValueError, TypeError): pass
    return jsonify({'results': results, 'count': len(results), 'origin': origin,
        'destination': destination, 'departure_date': departure_date, 'passengers': passengers, 'cabin': cabin})

@bp.route('/search/ai', methods=['POST'])
def ai_search():
    data = request.get_json()
    query = data.get('query', '').strip()
    if not query: return jsonify({'error': 'query is required'}), 400
    parsed = parse_natural_language(query)
    if not parsed['origin'] or not parsed['destination']:
        return jsonify({'parsed': parsed, 'results': [],
            'suggestion': 'Could not identify origin or destination. Try: "flight from Lagos to London next month"'})
    results = search_flights(parsed['origin'], parsed['destination'], parsed['departure_date'],
        parsed['passengers'], parsed['cabin'])
    if parsed.get('budget_max_usd'):
        results = [r for r in results if r['pricing']['total'] <= parsed['budget_max_usd']]
    return jsonify({'parsed': parsed, 'results': results, 'count': len(results)})

@bp.route('/search/multicity', methods=['POST'])
def multicity_search():
    data = request.get_json()
    legs = data.get('legs', [])
    passengers = max(1, min(int(data.get('passengers', 1)), 9))
    cabin = data.get('cabin', 'economy')
    if len(legs) < 2: return jsonify({'error': 'At least 2 legs required'}), 400
    if len(legs) > 6: return jsonify({'error': 'Maximum 6 legs allowed'}), 400
    results = []
    for i, leg in enumerate(legs):
        origin = leg.get('origin', '').upper()
        destination = leg.get('destination', '').upper()
        date = leg.get('date', '')
        if not origin or not destination or not date:
            return jsonify({'error': f'Leg {i+1}: origin, destination, and date required'}), 400
        flights = search_flights(origin, destination, date, passengers, cabin)
        results.append({'leg_num': i + 1, 'origin': origin, 'destination': destination, 'date': date, 'flights': flights})
    return jsonify({'legs': results, 'passengers': passengers, 'cabin': cabin})

@bp.route('/featured', methods=['GET'])
def featured(): return jsonify(get_featured_routes())

@bp.route('/airports', methods=['GET'])
def airports(): return jsonify(get_airports())

@bp.route('/pricing/calculate', methods=['POST'])
def calculate_price():
    data = request.get_json()
    base_fare = data.get('base_fare')
    if base_fare is None: return jsonify({'error': 'base_fare required'}), 400
    result = calculate_total(float(base_fare), int(data.get('passengers', 1)),
        data.get('baggage', 'carry_on'), data.get('seat', 'standard'))
    return jsonify(result)

@bp.route('/pricing/options', methods=['GET'])
def pricing_options():
    return jsonify({
        'baggage': [{'id': k, 'label': k.replace('_', ' ').title(), 'fee_usd': v} for k, v in BAGGAGE_FEES.items()],
        'seats': [{'id': k, 'label': k.replace('_', ' ').title(), 'fee_usd': v} for k, v in SEAT_FEES.items()],
    })
```

## FILE: backend/routes/bookings.py
```python
import json, random, string
from flask import Blueprint, request, jsonify, g
from backend.models.database import db
from backend.models.booking import Booking, BookingStatus, generate_reference
from backend.models.user import User
from backend.middleware.jwt_guard import jwt_required
from backend.services.pricing import calculate_total
from backend.services.email_service import send_booking_confirmation_email

bp = Blueprint('bookings', __name__, url_prefix='/api/bookings')

@bp.route('', methods=['POST'])
@jwt_required
def create_booking():
    data = request.get_json()
    required = ['flight_id', 'origin', 'destination', 'departure_date', 'airline', 'base_fare', 'passengers']
    if not all(data.get(f) for f in required):
        return jsonify({'error': f'Required fields: {", ".join(required)}'}), 400
    pricing = calculate_total(float(data['base_fare']), len(data['passengers']),
        data.get('baggage', 'carry_on'), data.get('seat', 'standard'))
    ref = generate_reference()
    while Booking.query.filter_by(reference=ref).first(): ref = generate_reference()
    booking = Booking(reference=ref, user_id=g.user_id, flight_id=data['flight_id'],
        origin=data['origin'].upper(), destination=data['destination'].upper(),
        departure_date=data['departure_date'], airline=data['airline'],
        flight_number=data.get('flight_number'), cabin_class=data.get('cabin', 'economy'),
        passengers_json=json.dumps(data['passengers']), passenger_count=len(data['passengers']),
        base_fare_usd=pricing['base_fare'], markup_usd=pricing['markup'],
        service_fee_usd=pricing['service_fee'], baggage_fee_usd=pricing['baggage_fee'],
        seat_fee_usd=pricing['seat_fee'], total_usd=pricing['total'],
        commission_usd=pricing['commission'], status=BookingStatus.CONFIRMED)
    db.session.add(booking)
    db.session.commit()
    user = User.query.get(g.user_id)
    if user: send_booking_confirmation_email(user.email, user.first_name, booking.to_dict())
    return jsonify({'booking': booking.to_dict(), 'message': 'Booking confirmed!'}), 201

@bp.route('/multicity', methods=['POST'])
@jwt_required
def create_multicity_booking():
    data = request.get_json()
    legs = data.get('legs', [])
    passengers = data.get('passengers', [])
    baggage = data.get('baggage', 'carry_on')
    seat = data.get('seat', 'standard')
    cabin = data.get('cabin', 'economy')
    if len(legs) < 2: return jsonify({'error': 'At least 2 legs required for multi-city booking'}), 400
    if not passengers: return jsonify({'error': 'passengers required'}), 400
    group_ref = 'AF' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    created = []
    combined_total = 0.0
    for leg in legs:
        pricing = calculate_total(float(leg['base_fare']), len(passengers), baggage, seat)
        ref = generate_reference()
        while Booking.query.filter_by(reference=ref).first(): ref = generate_reference()
        booking = Booking(reference=ref, user_id=g.user_id, flight_id=leg['flight_id'],
            origin=leg['origin'].upper(), destination=leg['destination'].upper(),
            departure_date=leg['date'], airline=leg['airline'],
            flight_number=leg.get('flight_number'), cabin_class=cabin,
            passengers_json=json.dumps(passengers), passenger_count=len(passengers),
            base_fare_usd=pricing['base_fare'], markup_usd=pricing['markup'],
            service_fee_usd=pricing['service_fee'], baggage_fee_usd=pricing['baggage_fee'],
            seat_fee_usd=pricing['seat_fee'], total_usd=pricing['total'],
            commission_usd=pricing['commission'], group_reference=group_ref,
            is_multicity=True, status=BookingStatus.CONFIRMED)
        db.session.add(booking)
        created.append(booking)
        combined_total += pricing['total']
    db.session.commit()
    user = User.query.get(g.user_id)
    if user and created: send_booking_confirmation_email(user.email, user.first_name, created[0].to_dict())
    return jsonify({'group_reference': group_ref, 'bookings': [b.to_dict() for b in created],
        'total_legs': len(created), 'combined_total_usd': round(combined_total, 2),
        'message': f'Multi-city booking confirmed! {len(created)} flights booked.'}), 201

@bp.route('', methods=['GET'])
@jwt_required
def my_bookings():
    if g.role == 'customer':
        bookings = Booking.query.filter_by(user_id=g.user_id).order_by(Booking.created_at.desc()).all()
    else:
        bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return jsonify([b.to_dict() for b in bookings])

@bp.route('/<booking_id>', methods=['GET'])
@jwt_required
def get_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if g.role == 'customer' and booking.user_id != g.user_id:
        return jsonify({'error': 'Access denied'}), 403
    return jsonify(booking.to_dict())

@bp.route('/<booking_id>/cancel', methods=['POST'])
@jwt_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if g.role == 'customer' and booking.user_id != g.user_id:
        return jsonify({'error': 'Access denied'}), 403
    if booking.status == BookingStatus.CANCELLED:
        return jsonify({'error': 'Booking already cancelled'}), 400
    booking.status = BookingStatus.CANCELLED
    db.session.commit()
    return jsonify({'message': 'Booking cancelled', 'booking': booking.to_dict()})
```

## FILE: backend/routes/admin.py
```python
from flask import Blueprint, jsonify, request, g
from backend.models.database import db
from backend.models.user import User
from backend.models.staff import Staff, StaffRole
from backend.models.booking import Booking, BookingStatus
from backend.middleware.role_guard import require_role
from sqlalchemy import func

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@bp.route('/dashboard', methods=['GET'])
@require_role('super_admin', 'admin', 'agent', 'finance')
def dashboard():
    total_bookings = Booking.query.count()
    confirmed = Booking.query.filter_by(status=BookingStatus.CONFIRMED).count()
    cancelled = Booking.query.filter_by(status=BookingStatus.CANCELLED).count()
    total_revenue = db.session.query(func.sum(Booking.total_usd)).filter_by(status=BookingStatus.CONFIRMED).scalar() or 0
    total_commission = db.session.query(func.sum(Booking.commission_usd)).filter_by(status=BookingStatus.CONFIRMED).scalar() or 0
    total_customers = User.query.count()
    total_staff = Staff.query.count()
    data = {'bookings': {'total': total_bookings, 'confirmed': confirmed, 'cancelled': cancelled,
            'pending': total_bookings - confirmed - cancelled},
        'revenue': {'total_usd': round(total_revenue, 2), 'commission_usd': round(total_commission, 2),
            'service_fees_usd': round(confirmed * 15, 2)},
        'customers': total_customers}
    if g.role in ('super_admin', 'admin'): data['staff'] = total_staff
    return jsonify(data)

@bp.route('/customers', methods=['GET'])
@require_role('super_admin', 'admin', 'agent')
def customers():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    search = request.args.get('search', '')
    query = User.query
    if search:
        query = query.filter((User.email.ilike(f'%{search}%')) |
            (User.first_name.ilike(f'%{search}%')) | (User.last_name.ilike(f'%{search}%')))
    paginated = query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page)
    customers_data = []
    for u in paginated.items:
        d = u.to_dict()
        d['booking_count'] = Booking.query.filter_by(user_id=u.id).count()
        d['total_spent'] = round(db.session.query(func.sum(Booking.total_usd))
            .filter_by(user_id=u.id, status=BookingStatus.CONFIRMED).scalar() or 0, 2)
        customers_data.append(d)
    return jsonify({'customers': customers_data, 'total': paginated.total,
        'pages': paginated.pages, 'page': page})

@bp.route('/bookings', methods=['GET'])
@require_role('super_admin', 'admin', 'agent', 'finance')
def all_bookings():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    status_filter = request.args.get('status')
    query = Booking.query
    if status_filter:
        try: query = query.filter_by(status=BookingStatus(status_filter))
        except ValueError: pass
    paginated = query.order_by(Booking.created_at.desc()).paginate(page=page, per_page=per_page)
    return jsonify({'bookings': [b.to_dict() for b in paginated.items],
        'total': paginated.total, 'pages': paginated.pages, 'page': page})

@bp.route('/bookings/<booking_id>', methods=['PUT'])
@require_role('super_admin', 'admin', 'agent')
def update_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    data = request.get_json()
    if 'status' in data:
        try: booking.status = BookingStatus(data['status'])
        except ValueError: return jsonify({'error': 'Invalid status'}), 400
    if 'notes' in data: booking.notes = data['notes']
    db.session.commit()
    return jsonify(booking.to_dict())

@bp.route('/finance/summary', methods=['GET'])
@require_role('super_admin', 'admin', 'finance')
def finance_summary():
    confirmed_bookings = Booking.query.filter_by(status=BookingStatus.CONFIRMED).all()
    total_revenue = sum(b.total_usd for b in confirmed_bookings)
    total_commission = sum(b.commission_usd for b in confirmed_bookings)
    total_markup = sum(b.markup_usd for b in confirmed_bookings)
    total_service_fees = sum(b.service_fee_usd for b in confirmed_bookings)
    total_baggage = sum(b.baggage_fee_usd for b in confirmed_bookings)
    return jsonify({'total_revenue_usd': round(total_revenue, 2), 'commission_usd': round(total_commission, 2),
        'markup_usd': round(total_markup, 2), 'service_fees_usd': round(total_service_fees, 2),
        'baggage_fees_usd': round(total_baggage, 2), 'total_bookings': len(confirmed_bookings),
        'avg_booking_value': round(total_revenue / max(len(confirmed_bookings), 1), 2)})

@bp.route('/settings', methods=['GET'])
@require_role('super_admin')
def get_settings():
    from backend.config import Config
    return jsonify({'markup_percent': Config.MARKUP_PERCENT, 'service_fee_usd': Config.SERVICE_FEE_USD,
        'commission_percent': Config.COMMISSION_PERCENT})
```

## FILE: backend/routes/staff_mgmt.py
```python
import bcrypt, secrets, string
from flask import Blueprint, request, jsonify, g
from backend.models.database import db
from backend.models.staff import Staff, StaffRole, can_manage
from backend.middleware.role_guard import require_role
from backend.services.email_service import send_staff_credentials_email

bp = Blueprint('staff_mgmt', __name__, url_prefix='/api/admin/staff')

@bp.route('', methods=['GET'])
@require_role('super_admin', 'admin')
def list_staff():
    return jsonify([s.to_dict() for s in Staff.query.order_by(Staff.created_at.desc()).all()])

@bp.route('', methods=['POST'])
@require_role('super_admin', 'admin')
def create_staff():
    data = request.get_json()
    required = ['email', 'first_name', 'last_name', 'role']
    if not all(data.get(f) for f in required):
        return jsonify({'error': f'Required: {", ".join(required)}'}), 400
    try: role = StaffRole(data['role'])
    except ValueError: return jsonify({'error': f'Invalid role. Valid: {[r.value for r in StaffRole]}'}), 400
    actor_role = StaffRole(g.role)
    if not can_manage(actor_role, role):
        return jsonify({'error': 'Cannot assign a role equal to or above your own'}), 403
    if Staff.query.filter_by(email=data['email'].lower()).first():
        return jsonify({'error': 'Email already registered'}), 409
    temp_password = _generate_temp_password()
    hashed = bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt())
    staff = Staff(email=data['email'].lower(), password_hash=hashed.decode('utf-8'),
        first_name=data['first_name'], last_name=data['last_name'], role=role,
        must_change_password=True, is_active=True, created_by=g.user_id)
    db.session.add(staff)
    db.session.commit()
    send_staff_credentials_email(staff.email, staff.first_name, role.value, temp_password)
    return jsonify({'message': 'Staff account created. Credentials sent to email.',
        'staff': staff.to_dict(), 'temp_password': temp_password}), 201

@bp.route('/<staff_id>', methods=['GET'])
@require_role('super_admin', 'admin')
def get_staff(staff_id):
    return jsonify(Staff.query.get_or_404(staff_id).to_dict())

@bp.route('/<staff_id>', methods=['PUT'])
@require_role('super_admin', 'admin')
def update_staff(staff_id):
    staff = Staff.query.get_or_404(staff_id)
    actor_role = StaffRole(g.role)
    if not can_manage(actor_role, staff.role):
        return jsonify({'error': 'Cannot modify staff with equal or higher role'}), 403
    data = request.get_json()
    if 'role' in data:
        try: new_role = StaffRole(data['role'])
        except ValueError: return jsonify({'error': 'Invalid role'}), 400
        if not can_manage(actor_role, new_role):
            return jsonify({'error': 'Cannot assign role equal to or above your own'}), 403
        staff.role = new_role
    if 'first_name' in data: staff.first_name = data['first_name']
    if 'last_name' in data: staff.last_name = data['last_name']
    if 'is_active' in data: staff.is_active = bool(data['is_active'])
    db.session.commit()
    return jsonify(staff.to_dict())

@bp.route('/<staff_id>/reset-password', methods=['POST'])
@require_role('super_admin', 'admin')
def reset_staff_password(staff_id):
    staff = Staff.query.get_or_404(staff_id)
    actor_role = StaffRole(g.role)
    if not can_manage(actor_role, staff.role):
        return jsonify({'error': 'Cannot reset password for staff with equal or higher role'}), 403
    temp_password = _generate_temp_password()
    hashed = bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt())
    staff.password_hash = hashed.decode('utf-8')
    staff.must_change_password = True
    db.session.commit()
    send_staff_credentials_email(staff.email, staff.first_name, staff.role.value, temp_password)
    return jsonify({'message': 'Password reset. New credentials sent to staff email.', 'temp_password': temp_password})

@bp.route('/<staff_id>', methods=['DELETE'])
@require_role('super_admin')
def delete_staff(staff_id):
    if staff_id == g.user_id: return jsonify({'error': 'Cannot delete your own account'}), 400
    staff = Staff.query.get_or_404(staff_id)
    staff.is_active = False
    db.session.commit()
    return jsonify({'message': 'Staff account deactivated'})

def _generate_temp_password():
    chars = string.ascii_letters + string.digits + '!@#$%'
    return ''.join(secrets.choice(chars) for _ in range(12))
```

## FILE: backend/services/mock_flights.py
```python
import random
from datetime import datetime, timedelta

AIRLINES = [
    {'name': 'Air Peace', 'code': 'P4', 'region': 'africa', 'trust_score': 4.1},
    {'name': 'Ethiopian Airlines', 'code': 'ET', 'region': 'africa', 'trust_score': 4.7},
    {'name': 'Kenya Airways', 'code': 'KQ', 'region': 'africa', 'trust_score': 4.3},
    {'name': 'RwandAir', 'code': 'WB', 'region': 'africa', 'trust_score': 4.5},
    {'name': 'Arik Air', 'code': 'W3', 'region': 'africa', 'trust_score': 3.8},
    {'name': 'IbomAir', 'code': 'Z9', 'region': 'africa', 'trust_score': 4.0},
    {'name': 'Emirates', 'code': 'EK', 'region': 'global', 'trust_score': 4.9},
    {'name': 'British Airways', 'code': 'BA', 'region': 'global', 'trust_score': 4.6},
    {'name': 'Turkish Airlines', 'code': 'TK', 'region': 'global', 'trust_score': 4.5},
    {'name': 'Qatar Airways', 'code': 'QR', 'region': 'global', 'trust_score': 4.8},
    {'name': 'Air France', 'code': 'AF', 'region': 'global', 'trust_score': 4.4},
    {'name': 'KLM', 'code': 'KL', 'region': 'global', 'trust_score': 4.5},
    {'name': 'Lufthansa', 'code': 'LH', 'region': 'global', 'trust_score': 4.6},
    {'name': 'South African Airways', 'code': 'SA', 'region': 'africa', 'trust_score': 4.2},
]

AIRPORTS = {
    'LOS': {'name': 'Murtala Muhammed International', 'city': 'Lagos', 'country': 'Nigeria', 'region': 'africa'},
    'ABV': {'name': 'Nnamdi Azikiwe International', 'city': 'Abuja', 'country': 'Nigeria', 'region': 'africa'},
    'PHC': {'name': 'Port Harcourt International', 'city': 'Port Harcourt', 'country': 'Nigeria', 'region': 'africa'},
    'ACC': {'name': 'Kotoka International', 'city': 'Accra', 'country': 'Ghana', 'region': 'africa'},
    'NBO': {'name': 'Jomo Kenyatta International', 'city': 'Nairobi', 'country': 'Kenya', 'region': 'africa'},
    'ADD': {'name': 'Bole International', 'city': 'Addis Ababa', 'country': 'Ethiopia', 'region': 'africa'},
    'JNB': {'name': 'O.R. Tambo International', 'city': 'Johannesburg', 'country': 'South Africa', 'region': 'africa'},
    'CMN': {'name': 'Mohammed V International', 'city': 'Casablanca', 'country': 'Morocco', 'region': 'africa'},
    'KGL': {'name': 'Kigali International', 'city': 'Kigali', 'country': 'Rwanda', 'region': 'africa'},
    'DKR': {'name': 'Blaise Diagne International', 'city': 'Dakar', 'country': 'Senegal', 'region': 'africa'},
    'DXB': {'name': 'Dubai International', 'city': 'Dubai', 'country': 'UAE', 'region': 'middle_east'},
    'DOH': {'name': 'Hamad International', 'city': 'Doha', 'country': 'Qatar', 'region': 'middle_east'},
    'LHR': {'name': 'Heathrow Airport', 'city': 'London', 'country': 'UK', 'region': 'europe'},
    'CDG': {'name': 'Charles de Gaulle', 'city': 'Paris', 'country': 'France', 'region': 'europe'},
    'AMS': {'name': 'Amsterdam Schiphol', 'city': 'Amsterdam', 'country': 'Netherlands', 'region': 'europe'},
    'FRA': {'name': 'Frankfurt Airport', 'city': 'Frankfurt', 'country': 'Germany', 'region': 'europe'},
    'IST': {'name': 'Istanbul Airport', 'city': 'Istanbul', 'country': 'Turkey', 'region': 'europe'},
    'JFK': {'name': 'John F. Kennedy International', 'city': 'New York', 'country': 'USA', 'region': 'americas'},
    'IAD': {'name': 'Dulles International', 'city': 'Washington DC', 'country': 'USA', 'region': 'americas'},
    'YYZ': {'name': 'Toronto Pearson International', 'city': 'Toronto', 'country': 'Canada', 'region': 'americas'},
}

BASE_PRICES = {
    ('LOS', 'ABV'): (80, 150), ('LOS', 'PHC'): (90, 180), ('ABV', 'PHC'): (70, 140),
    ('LOS', 'ACC'): (200, 450), ('ABV', 'ACC'): (220, 480),
    ('LOS', 'NBO'): (350, 700), ('LOS', 'ADD'): (380, 750), ('LOS', 'JNB'): (400, 800),
    ('NBO', 'ADD'): (150, 300), ('NBO', 'JNB'): (250, 500),
    ('LOS', 'CMN'): (300, 600),
    ('LOS', 'DXB'): (450, 900), ('LOS', 'DOH'): (470, 950), ('ABV', 'DXB'): (430, 880),
    ('LOS', 'LHR'): (550, 1100), ('LOS', 'CDG'): (580, 1150), ('LOS', 'AMS'): (560, 1120),
    ('LOS', 'FRA'): (570, 1130), ('LOS', 'IST'): (480, 960), ('ABV', 'LHR'): (530, 1080),
    ('LOS', 'JFK'): (750, 1500), ('LOS', 'IAD'): (720, 1450),
    ('ACC', 'NBO'): (280, 560), ('ADD', 'JNB'): (300, 600),
    ('KGL', 'NBO'): (120, 240), ('DKR', 'ACC'): (180, 360),
}

CABINS = {'economy': 1.0, 'premium_economy': 1.8, 'business': 3.5, 'first': 6.0}
STOPS = [{'stops': 0, 'label': 'Nonstop'}, {'stops': 1, 'label': '1 Stop'}, {'stops': 2, 'label': '2 Stops'}]
OTA_PROVIDERS = [
    {'id': 'ota_1', 'name': 'TravelEase', 'trust_score': 4.8, 'verified': True, 'reviews': 12400},
    {'id': 'ota_2', 'name': 'FlyDirect', 'trust_score': 4.2, 'verified': True, 'reviews': 7300},
    {'id': 'ota_3', 'name': 'BudgetWings', 'trust_score': 3.5, 'verified': False, 'reviews': 2100},
]

def search_flights(origin, destination, departure_date, passengers=1, cabin='economy', return_date=None):
    key = (origin.upper(), destination.upper())
    rev_key = (destination.upper(), origin.upper())
    price_range = BASE_PRICES.get(key) or BASE_PRICES.get(rev_key) or (300, 900)
    cabin_mult = CABINS.get(cabin, 1.0)
    results = []
    num_results = random.randint(3, 6)
    used_airlines = random.sample(AIRLINES, min(num_results, len(AIRLINES)))
    for i, airline in enumerate(used_airlines):
        base = round(random.uniform(price_range[0], price_range[1]) * cabin_mult, 2)
        stops_info = random.choice(STOPS) if i > 0 else STOPS[0]
        dep_hour = random.randint(5, 22)
        dep_min = random.choice([0, 15, 30, 45])
        duration_hrs = _estimate_duration(origin, destination, stops_info['stops'])
        arr_hour = (dep_hour + duration_hrs) % 24
        flight_num = f"{airline['code']}{random.randint(100, 999)}"
        result = {
            'id': f"{flight_num}-{departure_date}-{i}",
            'airline': airline['name'], 'airline_code': airline['code'],
            'airline_region': airline['region'], 'flight_number': flight_num,
            'origin': origin.upper(), 'destination': destination.upper(),
            'origin_airport': AIRPORTS.get(origin.upper(), {}).get('name', origin),
            'destination_airport': AIRPORTS.get(destination.upper(), {}).get('name', destination),
            'departure_date': departure_date,
            'departure_time': f"{dep_hour:02d}:{dep_min:02d}",
            'arrival_time': f"{arr_hour:02d}:{dep_min:02d}",
            'duration_hours': duration_hrs, 'stops': stops_info['stops'],
            'stops_label': stops_info['label'], 'cabin': cabin, 'passengers': passengers,
            'is_africa_route': airline['region'] == 'africa',
            'airline_trust_score': airline['trust_score'],
            'pricing': _build_pricing(base, passengers),
            'ota_options': _get_ota_options(base, passengers),
            'available_seats': random.randint(3, 45),
            'baggage_included': cabin != 'economy',
        }
        if return_date:
            ret_base = round(base * random.uniform(0.85, 1.15), 2)
            result['return_flight'] = {'date': return_date,
                'departure_time': f"{random.randint(6, 22):02d}:00",
                'pricing': _build_pricing(ret_base, passengers)}
        results.append(result)
    results.sort(key=lambda x: x['pricing']['total'])
    return results

def _build_pricing(base_usd, passengers):
    from backend.config import Config
    markup = round(base_usd * (Config.MARKUP_PERCENT / 100), 2)
    service_fee = Config.SERVICE_FEE_USD
    commission = round(base_usd * (Config.COMMISSION_PERCENT / 100), 2)
    subtotal = base_usd + markup + service_fee
    total = round(subtotal * passengers, 2)
    return {'base_fare': base_usd, 'markup': markup, 'service_fee': service_fee,
        'baggage_fee': 0, 'seat_fee': 0, 'commission': commission,
        'subtotal_per_pax': round(subtotal, 2), 'total': total,
        'currency': 'USD', 'per_passenger': round(subtotal, 2)}

def _get_ota_options(base, passengers):
    options = []
    for ota in OTA_PROVIDERS:
        variation = random.uniform(-0.03, 0.08)
        ota_price = round(base * (1 + variation) * passengers, 2)
        options.append({'ota_id': ota['id'], 'ota_name': ota['name'], 'trust_score': ota['trust_score'],
            'verified': ota['verified'], 'reviews': ota['reviews'], 'price': ota_price})
    options.sort(key=lambda x: x['price'])
    return options

def _estimate_duration(origin, destination, stops):
    short_routes = {('LOS', 'ABV'), ('LOS', 'PHC'), ('ABV', 'PHC'), ('NBO', 'ADD'), ('KGL', 'NBO')}
    key = (origin.upper(), destination.upper())
    rev = (destination.upper(), origin.upper())
    if key in short_routes or rev in short_routes: base = 1
    elif origin in ('LOS', 'ABV') and destination in ('JFK', 'IAD', 'YYZ'): base = 10
    elif origin in ('LOS', 'ABV') and destination in ('LHR', 'CDG', 'AMS', 'FRA', 'IST'): base = 6
    elif origin in ('LOS', 'ABV') and destination in ('DXB', 'DOH'): base = 7
    else: base = 4
    return base + (stops * random.randint(1, 2))

def get_featured_routes():
    return [
        {'origin': 'LOS', 'destination': 'LHR', 'price_from': 549, 'airline': 'British Airways', 'label': 'Lagos → London'},
        {'origin': 'LOS', 'destination': 'DXB', 'price_from': 420, 'airline': 'Emirates', 'label': 'Lagos → Dubai'},
        {'origin': 'ABV', 'destination': 'NBO', 'price_from': 310, 'airline': 'Ethiopian Airlines', 'label': 'Abuja → Nairobi'},
        {'origin': 'LOS', 'destination': 'JFK', 'price_from': 720, 'airline': 'Air Peace', 'label': 'Lagos → New York'},
        {'origin': 'ACC', 'destination': 'ADD', 'price_from': 280, 'airline': 'RwandAir', 'label': 'Accra → Addis Ababa'},
        {'origin': 'NBO', 'destination': 'JNB', 'price_from': 240, 'airline': 'Kenya Airways', 'label': 'Nairobi → Johannesburg'},
    ]

def get_airports():
    return [{'code': k, **v} for k, v in AIRPORTS.items()]
```

## FILE: backend/services/pricing.py
```python
from backend.config import Config

BAGGAGE_FEES = {'carry_on': 0, 'checked_1': 35, 'checked_2': 60}
SEAT_FEES = {'standard': 0, 'extra_legroom': 45, 'front_row': 30, 'window': 15, 'aisle': 10}

def calculate_total(base_fare, passengers=1, baggage_option='carry_on', seat_option='standard',
                    markup_pct=None, service_fee=None, commission_pct=None):
    markup_pct = markup_pct if markup_pct is not None else Config.MARKUP_PERCENT
    service_fee = service_fee if service_fee is not None else Config.SERVICE_FEE_USD
    commission_pct = commission_pct if commission_pct is not None else Config.COMMISSION_PERCENT
    markup = round(base_fare * (markup_pct / 100), 2)
    baggage_fee = BAGGAGE_FEES.get(baggage_option, 0) * passengers
    seat_fee = SEAT_FEES.get(seat_option, 0) * passengers
    commission = round(base_fare * (commission_pct / 100), 2)
    subtotal = base_fare + markup + service_fee + baggage_fee + seat_fee
    total = round(subtotal * passengers, 2)
    return {'base_fare': base_fare, 'markup': markup, 'markup_pct': markup_pct,
        'service_fee': service_fee, 'baggage_fee': baggage_fee, 'seat_fee': seat_fee,
        'commission': commission, 'commission_pct': commission_pct,
        'subtotal_per_pax': round(base_fare + markup + service_fee + (baggage_fee/passengers) + (seat_fee/passengers), 2),
        'total': total, 'passengers': passengers, 'currency': 'USD'}
```

## FILE: backend/services/ai_search.py
```python
import re

CITY_TO_IATA = {
    'lagos': 'LOS', 'abuja': 'ABV', 'port harcourt': 'PHC',
    'accra': 'ACC', 'nairobi': 'NBO', 'addis ababa': 'ADD',
    'johannesburg': 'JNB', 'joburg': 'JNB', 'jnb': 'JNB',
    'casablanca': 'CMN', 'kigali': 'KGL', 'dakar': 'DKR',
    'dubai': 'DXB', 'doha': 'DOH',
    'london': 'LHR', 'paris': 'CDG', 'amsterdam': 'AMS',
    'frankfurt': 'FRA', 'istanbul': 'IST',
    'new york': 'JFK', 'nyc': 'JFK', 'washington': 'IAD', 'toronto': 'YYZ',
}
MONTH_MAP = {
    'january': '01', 'february': '02', 'march': '03', 'april': '04',
    'may': '05', 'june': '06', 'july': '07', 'august': '08',
    'september': '09', 'october': '10', 'november': '11', 'december': '12',
    'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
    'jun': '06', 'jul': '07', 'aug': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12',
}
CABIN_KEYWORDS = {
    'business': 'business', 'business class': 'business',
    'first class': 'first', 'first': 'first',
    'premium economy': 'premium_economy', 'premium': 'premium_economy',
    'economy': 'economy', 'cheap': 'economy', 'budget': 'economy',
}

def parse_natural_language(query: str) -> dict:
    q = query.lower().strip()
    result = {'origin': None, 'destination': None, 'departure_date': None, 'return_date': None,
        'passengers': 1, 'cabin': 'economy', 'budget_max_usd': None, 'raw_query': query}
    iata_codes = re.findall(r'\b([A-Z]{3})\b', query.upper())
    cities_found = [code for city, code in CITY_TO_IATA.items() if city in q]
    all_codes = iata_codes + [c for c in cities_found if c not in iata_codes]
    to_match = re.search(r'(?:from\s+(\w[\w\s]+?)\s+to\s+(\w[\w\s]+?))\s', q + ' ')
    if to_match:
        src = _city_to_code(to_match.group(1).strip())
        dst = _city_to_code(to_match.group(2).strip())
        if src: result['origin'] = src
        if dst: result['destination'] = dst
    elif len(all_codes) >= 2:
        result['origin'] = all_codes[0]; result['destination'] = all_codes[1]
    elif len(all_codes) == 1:
        result['destination'] = all_codes[0]
    from datetime import datetime, timedelta
    today = datetime.utcnow()
    if 'next month' in q:
        d = today.replace(day=1) + timedelta(days=32)
        result['departure_date'] = d.replace(day=15).strftime('%Y-%m-%d')
    elif 'this month' in q:
        result['departure_date'] = (today + timedelta(days=7)).strftime('%Y-%m-%d')
    else:
        for month_name, month_num in MONTH_MAP.items():
            if month_name in q:
                year = today.year if int(month_num) >= today.month else today.year + 1
                result['departure_date'] = f"{year}-{month_num}-15"
                break
    if not result['departure_date']:
        result['departure_date'] = (today + timedelta(days=14)).strftime('%Y-%m-%d')
    pax_match = re.search(r'(\d+)\s*(?:passenger|people|person|adult|pax)', q)
    if pax_match: result['passengers'] = min(int(pax_match.group(1)), 9)
    for keyword, cabin in CABIN_KEYWORDS.items():
        if keyword in q: result['cabin'] = cabin; break
    budget_match = re.search(r'(?:under|below|max|budget)\s*[\$£₦]?\s*([\d,]+)', q)
    if budget_match:
        amount = int(budget_match.group(1).replace(',', ''))
        if '₦' in query or 'naira' in q or amount > 100000: amount = round(amount / 1500)
        result['budget_max_usd'] = amount
    return result

def _city_to_code(name: str) -> str:
    return CITY_TO_IATA.get(name.strip().lower())
```

## FILE: backend/services/email_service.py
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

def send_email(to_email: str, subject: str, html_body: str):
    app = current_app._get_current_object()
    mail_user = app.config.get('MAIL_USERNAME')
    mail_pass = app.config.get('MAIL_PASSWORD')
    mail_server = app.config.get('MAIL_SERVER', 'smtp.gmail.com')
    mail_port = app.config.get('MAIL_PORT', 587)
    sender = app.config.get('MAIL_DEFAULT_SENDER', 'Airfinder <noreply@airfinder.com>')
    if not mail_user or not mail_pass or mail_pass == 'your-mail-password-here':
        msg = f"\n[EMAIL DEV MODE]\nTo: {to_email}\nSubject: {subject}\n"
        import sys
        sys.stdout.buffer.write(msg.encode('utf-8', errors='replace') + b"\n")
        sys.stdout.flush()
        return True
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject; msg['From'] = sender; msg['To'] = to_email
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        with smtplib.SMTP(mail_server, mail_port) as server:
            server.starttls(); server.login(mail_user, mail_pass)
            server.sendmail(mail_user, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}"); return False

def send_welcome_email(to_email: str, first_name: str):
    send_email(to_email, "Welcome to Airfinder",
        f'<div style="font-family:sans-serif;max-width:600px;margin:auto;"><h2 style="color:#407E3C;">Welcome to Airfinder, {first_name}!</h2><p>Your account is ready. Start searching for the best flights worldwide.</p><a href="http://localhost:5000" style="background:#407E3C;color:white;padding:12px 24px;text-decoration:none;border-radius:6px;display:inline-block;margin-top:16px;">Search Flights</a></div>')

def send_password_reset_email(to_email: str, first_name: str, reset_link: str):
    send_email(to_email, "Reset Your Airfinder Password",
        f'<div style="font-family:sans-serif;max-width:600px;margin:auto;"><h2 style="color:#407E3C;">Password Reset Request</h2><p>Hi {first_name}, we received a request to reset your Airfinder password.</p><a href="{reset_link}" style="background:#407E3C;color:white;padding:12px 24px;text-decoration:none;border-radius:6px;display:inline-block;margin-top:16px;">Reset Password</a><p style="color:#888;margin-top:16px;">This link expires in 15 minutes.</p></div>')

def send_staff_credentials_email(to_email: str, first_name: str, role: str, temp_password: str):
    send_email(to_email, "Your Airfinder Staff Account",
        f'<div style="font-family:sans-serif;max-width:600px;margin:auto;"><h2 style="color:#407E3C;">Welcome to the Airfinder Team, {first_name}!</h2><p>Role: <strong>{role.replace("_"," ").title()}</strong></p><div style="background:#f5f5f5;padding:16px;border-radius:8px;margin:16px 0;"><p><strong>Email:</strong> {to_email}</p><p><strong>Temp Password:</strong> <code>{temp_password}</code></p></div><p style="color:#d32f2f;"><strong>You must change this password on first login.</strong></p><a href="http://localhost:5000/admin/login" style="background:#407E3C;color:white;padding:12px 24px;text-decoration:none;border-radius:6px;display:inline-block;margin-top:16px;">Login to Staff Portal</a></div>')

def send_booking_confirmation_email(to_email: str, first_name: str, booking: dict):
    send_email(to_email, f"Booking Confirmed — {booking.get('reference','')}",
        f'<div style="font-family:sans-serif;max-width:600px;margin:auto;"><h2 style="color:#407E3C;">Booking Confirmed</h2><p>Hi {first_name}, your flight has been booked successfully.</p><div style="background:#f5f5f5;padding:16px;border-radius:8px;margin:16px 0;"><p><strong>Reference:</strong> {booking.get("reference")}</p><p><strong>Route:</strong> {booking.get("origin")} to {booking.get("destination")}</p><p><strong>Date:</strong> {booking.get("departure_date")}</p><p><strong>Total:</strong> ${booking.get("pricing",{}).get("total",0)}</p></div></div>')
```

## FILE: backend/tests/conftest.py
```python
import pytest, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from backend.app import create_app
from backend.models.database import db as _db

@pytest.fixture(scope='session')
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET'] = 'test-secret'
    return app

@pytest.fixture(scope='session')
def client(app): return app.test_client()

@pytest.fixture(autouse=True)
def clean_db(app):
    with app.app_context():
        _db.drop_all(); _db.create_all()
        from backend.models.database import _seed_super_admin
        _seed_super_admin(app)
    yield
    with app.app_context(): _db.session.remove()
```

---
*SKILL.md continues — frontend CSS, JS, and HTML files follow in separate append sections.*


---

## FILE: frontend/css/main.css
```css
:root {
  --green: #407E3C;
  --green-dark: #2d5c29;
  --green-light: #5a9e56;
  --green-pale: #e8f5e4;
  --white: #ffffff;
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-400: #9ca3af;
  --gray-600: #4b5563;
  --gray-800: #1f2937;
  --red: #dc2626;
  --amber: #f59e0b;
  --blue: #2563eb;
  --shadow-sm: 0 1px 3px rgba(0,0,0,.1);
  --shadow: 0 4px 16px rgba(0,0,0,.12);
  --shadow-lg: 0 8px 32px rgba(0,0,0,.16);
  --radius: 10px; --radius-sm: 6px; --radius-lg: 16px;
  --font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body { font-family: var(--font); color: var(--gray-800); background: var(--gray-50); line-height: 1.6; font-size: 15px; }
a { color: var(--green); text-decoration: none; }
a:hover { text-decoration: underline; }
h1 { font-size: 2.4rem; font-weight: 800; line-height: 1.2; }
h2 { font-size: 1.7rem; font-weight: 700; }
h3 { font-size: 1.2rem; font-weight: 600; }
.container { max-width: 1180px; margin: 0 auto; padding: 0 20px; }
.section { padding: 60px 0; }
.btn { display: inline-flex; align-items: center; gap: 8px; padding: 11px 22px; border-radius: var(--radius-sm); font-size: 15px; font-weight: 600; border: none; cursor: pointer; transition: all .18s ease; text-decoration: none; }
.btn-primary { background: var(--green); color: var(--white); }
.btn-primary:hover { background: var(--green-dark); text-decoration: none; color: var(--white); }
.btn-secondary { background: var(--white); color: var(--green); border: 2px solid var(--green); }
.btn-secondary:hover { background: var(--green-pale); text-decoration: none; }
.btn-danger { background: var(--red); color: var(--white); }
.btn-sm { padding: 7px 14px; font-size: 13px; }
.btn-lg { padding: 14px 28px; font-size: 17px; }
.btn-full { width: 100%; justify-content: center; }
.btn:disabled { opacity: .5; cursor: not-allowed; }
.form-group { margin-bottom: 18px; }
.form-label { display: block; font-size: 13px; font-weight: 600; color: var(--gray-600); margin-bottom: 6px; text-transform: uppercase; letter-spacing: .4px; }
.form-control { width: 100%; padding: 11px 14px; border: 1.5px solid var(--gray-200); border-radius: var(--radius-sm); font-size: 15px; color: var(--gray-800); background: var(--white); transition: border-color .15s; font-family: var(--font); }
.form-control:focus { outline: none; border-color: var(--green); box-shadow: 0 0 0 3px rgba(64,126,60,.12); }
.form-control::placeholder { color: var(--gray-400); }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 600px) { .form-row { grid-template-columns: 1fr; } }
.card { background: var(--white); border-radius: var(--radius); box-shadow: var(--shadow-sm); border: 1px solid var(--gray-200); }
.card-body { padding: 24px; }
.alert { padding: 12px 16px; border-radius: var(--radius-sm); font-size: 14px; margin-bottom: 16px; display: flex; align-items: flex-start; gap: 8px; }
.alert-error { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
.alert-success { background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; }
.alert-warning { background: #fffbeb; color: #92400e; border: 1px solid #fde68a; }
.alert-info { background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; }
.badge { display: inline-flex; align-items: center; gap: 4px; padding: 3px 9px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.badge-green { background: var(--green-pale); color: var(--green-dark); }
.badge-amber { background: #fffbeb; color: #92400e; }
.badge-red { background: #fef2f2; color: #991b1b; }
.badge-blue { background: #eff6ff; color: #1e40af; }
.badge-gray { background: var(--gray-100); color: var(--gray-600); }
.navbar { background: var(--white); border-bottom: 1px solid var(--gray-200); position: sticky; top: 0; z-index: 100; box-shadow: var(--shadow-sm); }
.navbar-inner { display: flex; align-items: center; justify-content: space-between; padding: 0 20px; height: 64px; max-width: 1180px; margin: 0 auto; }
.navbar-brand { font-size: 1.6rem; font-weight: 900; color: var(--green); text-decoration: none; }
.navbar-links { display: flex; align-items: center; gap: 8px; }
.navbar-link { color: var(--gray-600); font-weight: 500; padding: 6px 12px; border-radius: var(--radius-sm); transition: all .15s; }
.navbar-link:hover { color: var(--green); background: var(--green-pale); text-decoration: none; }
@media (max-width: 768px) { .navbar-links { display: none; } }
.footer { background: var(--gray-800); color: var(--gray-400); padding: 48px 0 24px; }
.footer-grid { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 40px; margin-bottom: 40px; }
.footer-brand { font-size: 1.4rem; font-weight: 900; color: var(--white); margin-bottom: 12px; }
.footer-title { color: var(--white); font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: .5px; margin-bottom: 14px; }
.footer-links { list-style: none; }
.footer-links li { margin-bottom: 8px; }
.footer-links a { color: var(--gray-400); font-size: 14px; }
.footer-links a:hover { color: var(--green-light); }
.footer-bottom { border-top: 1px solid #374151; padding-top: 20px; font-size: 13px; text-align: center; }
@media (max-width: 768px) { .footer-grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 480px) { .footer-grid { grid-template-columns: 1fr; } }
.spinner { width: 28px; height: 28px; border: 3px solid var(--gray-200); border-top-color: var(--green); border-radius: 50%; animation: spin .7s linear infinite; margin: 0 auto; }
@keyframes spin { to { transform: rotate(360deg); } }
.text-center { text-align: center; } .text-green { color: var(--green); } .text-gray { color: var(--gray-600); }
.text-sm { font-size: 13px; } .text-xs { font-size: 11px; } .fw-bold { font-weight: 700; }
.mt-1 { margin-top: 8px; } .mt-2 { margin-top: 16px; } .mt-3 { margin-top: 24px; } .mt-4 { margin-top: 32px; }
.mb-1 { margin-bottom: 8px; } .mb-2 { margin-bottom: 16px; } .mb-3 { margin-bottom: 24px; }
.flex { display: flex; } .flex-between { display: flex; justify-content: space-between; align-items: center; }
.gap-1 { gap: 8px; } .gap-2 { gap: 16px; }
.hidden { display: none !important; }
.w-full { width: 100%; }
.divider { border: none; border-top: 1px solid var(--gray-200); margin: 20px 0; }
```

## FILE: frontend/css/components.css
```css
/* ===== AUTH PAGES ===== */
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--green-dark) 0%, var(--green) 100%);
  padding: 20px;
}
.auth-card {
  background: var(--white);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  width: 100%;
  max-width: 440px;
  padding: 36px 36px 32px;
}
.auth-logo {
  text-align: center;
  margin-bottom: 28px;
}
.auth-logo-text {
  font-size: 2rem;
  font-weight: 900;
  color: var(--green);
}
.auth-logo-sub { font-size: 13px; color: var(--gray-400); margin-top: 4px; }
.auth-title { font-size: 1.4rem; font-weight: 800; margin-bottom: 6px; }
.auth-sub { font-size: 14px; color: var(--gray-400); margin-bottom: 24px; }
.auth-divider {
  text-align: center;
  color: var(--gray-400);
  font-size: 13px;
  margin: 16px 0;
  position: relative;
}
.auth-divider::before, .auth-divider::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 40%;
  height: 1px;
  background: var(--gray-200);
}
.auth-divider::before { left: 0; }
.auth-divider::after { right: 0; }
.auth-footer { text-align: center; margin-top: 20px; font-size: 14px; color: var(--gray-600); }
.password-toggle { position: relative; }
.password-toggle .toggle-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  color: var(--gray-400);
  font-size: 16px;
  padding: 4px;
}
.strength-bar { height: 4px; border-radius: 2px; background: var(--gray-200); margin-top: 6px; overflow: hidden; }
.strength-fill { height: 100%; border-radius: 2px; transition: width .3s, background .3s; }

/* ===== ACCOUNT DASHBOARD ===== */
.account-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 24px;
  padding: 32px 0;
}
@media (max-width: 760px) { .account-layout { grid-template-columns: 1fr; } }

.account-sidebar {
  background: var(--white);
  border-radius: var(--radius);
  border: 1px solid var(--gray-200);
  padding: 24px;
  height: fit-content;
  position: sticky;
  top: 80px;
}
.account-avatar {
  width: 64px; height: 64px;
  background: var(--green);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--white);
  font-size: 1.4rem;
  font-weight: 800;
  margin: 0 auto 12px;
}
.account-name { text-align: center; font-weight: 700; margin-bottom: 4px; }
.account-email { text-align: center; font-size: 13px; color: var(--gray-400); margin-bottom: 20px; }
.account-nav { list-style: none; }
.account-nav li { margin-bottom: 4px; }
.account-nav a {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: var(--radius-sm);
  color: var(--gray-600);
  font-weight: 500;
  font-size: 14px;
  transition: all .15s;
}
.account-nav a:hover { background: var(--green-pale); color: var(--green); text-decoration: none; }
.account-nav a.active { background: var(--green-pale); color: var(--green); font-weight: 700; }

/* Booking Card */
.booking-card {
  background: var(--white);
  border-radius: var(--radius);
  border: 1px solid var(--gray-200);
  margin-bottom: 12px;
  overflow: hidden;
}
.booking-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--gray-100);
}
.booking-ref { font-weight: 800; font-family: monospace; font-size: 15px; letter-spacing: .5px; }
.booking-card-body { padding: 16px 20px; }
.booking-route { font-size: 1.1rem; font-weight: 700; margin-bottom: 4px; }
.booking-detail { font-size: 13px; color: var(--gray-600); }

/* ===== BOOKING FLOW ===== */
.booking-steps {
  display: flex;
  align-items: center;
  gap: 0;
  margin-bottom: 32px;
  padding: 20px 0;
  overflow-x: auto;
}
.step {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
.step-num {
  width: 30px; height: 30px;
  border-radius: 50%;
  background: var(--gray-200);
  color: var(--gray-400);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 13px;
}
.step.active .step-num { background: var(--green); color: var(--white); }
.step.done .step-num { background: var(--green-light); color: var(--white); }
.step-label { font-size: 13px; font-weight: 600; color: var(--gray-400); }
.step.active .step-label { color: var(--green); }
.step-connector { width: 40px; height: 2px; background: var(--gray-200); flex-shrink: 0; }
.step.done + .step .step-connector { background: var(--green-light); }

.booking-layout { display: grid; grid-template-columns: 1fr 340px; gap: 24px; }
@media (max-width: 860px) { .booking-layout { grid-template-columns: 1fr; } }

.price-summary-card {
  background: var(--white);
  border-radius: var(--radius);
  border: 1px solid var(--gray-200);
  padding: 20px;
  position: sticky;
  top: 80px;
  height: fit-content;
}
.price-summary-title { font-weight: 700; margin-bottom: 16px; }
.price-line { display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 8px; color: var(--gray-600); }
.price-line.total { font-weight: 800; font-size: 1.1rem; color: var(--gray-800); padding-top: 12px; border-top: 1px solid var(--gray-200); margin-top: 4px; }
.price-transparency { background: var(--green-pale); border-radius: var(--radius-sm); padding: 10px 12px; margin-top: 12px; font-size: 12px; color: var(--green-dark); }

/* Passenger form */
.passenger-block {
  background: var(--gray-50);
  border-radius: var(--radius);
  padding: 20px;
  margin-bottom: 16px;
  border: 1px solid var(--gray-200);
}
.passenger-title { font-weight: 700; margin-bottom: 16px; font-size: 15px; }

/* Payment stub */
.card-input-group { position: relative; }
.card-icons { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); display: flex; gap: 6px; }
.card-icon { width: 32px; height: 20px; background: var(--gray-200); border-radius: 3px; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: 700; }

/* Confirmation */
.confirmation-icon {
  width: 80px; height: 80px;
  background: var(--green);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: var(--white);
  margin: 0 auto 20px;
}

/* ===== FEATURED ROUTES ===== */
.featured-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 14px;
}
.route-card {
  background: var(--white);
  border-radius: var(--radius);
  border: 1px solid var(--gray-200);
  padding: 18px;
  cursor: pointer;
  transition: all .18s;
}
.route-card:hover { border-color: var(--green); transform: translateY(-2px); box-shadow: var(--shadow); }
.route-from { font-size: 12px; color: var(--gray-400); text-transform: uppercase; letter-spacing: .5px; }
.route-to { font-size: 1rem; font-weight: 700; margin: 4px 0; }
.route-airline { font-size: 12px; color: var(--gray-600); }
.route-price { font-size: 1.2rem; font-weight: 900; color: var(--green); margin-top: 10px; }
.route-price-from { font-size: 11px; color: var(--gray-400); font-weight: 400; }

/* ===== HOW WE EARN (Transparency) ===== */
.transparency-section { background: var(--green-pale); }
.earn-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-top: 32px; }
.earn-card { background: var(--white); border-radius: var(--radius); padding: 20px; border: 1px solid rgba(64,126,60,.15); }
.earn-icon { font-size: 1.8rem; margin-bottom: 10px; }
.earn-label { font-weight: 700; margin-bottom: 6px; }
.earn-desc { font-size: 14px; color: var(--gray-600); }

/* ===== TRUST INDICATORS ===== */
.trust-bar { display: flex; justify-content: center; gap: 32px; flex-wrap: wrap; padding: 20px 0; }
.trust-item { display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 600; color: rgba(255,255,255,.9); }

/* ===== MODAL ===== */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  backdrop-filter: blur(2px);
}
.modal {
  background: var(--white);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  width: 100%;
  max-width: 480px;
  padding: 28px;
  position: relative;
}
.modal-close {
  position: absolute;
  top: 16px; right: 16px;
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: var(--gray-400);
}

```

## FILE: frontend/css/search.css
```css
/* ===== HERO ===== */
.hero {
  background: linear-gradient(135deg, var(--green-dark) 0%, var(--green) 60%, var(--green-light) 100%);
  padding: 72px 0 56px;
  color: var(--white);
  position: relative;
  overflow: hidden;
}
.hero::before {
  content: '';
  position: absolute;
  top: -60px; right: -80px;
  width: 400px; height: 400px;
  background: rgba(255,255,255,.06);
  border-radius: 50%;
}
.hero::after {
  content: '';
  position: absolute;
  bottom: -80px; left: -60px;
  width: 300px; height: 300px;
  background: rgba(255,255,255,.04);
  border-radius: 50%;
}
.hero-content { position: relative; z-index: 1; }
.hero-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(255,255,255,.15);
  border: 1px solid rgba(255,255,255,.25);
  border-radius: 20px;
  padding: 5px 14px;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 20px;
  backdrop-filter: blur(4px);
}
.hero h1 { font-size: 3rem; font-weight: 900; margin-bottom: 16px; }
.hero h1 em { font-style: normal; color: #a8f0a0; }
.hero-sub { font-size: 1.1rem; opacity: .88; margin-bottom: 40px; max-width: 560px; }

/* ===== AI SEARCH BAR ===== */
.ai-search-bar {
  background: rgba(255,255,255,.12);
  border: 1.5px solid rgba(255,255,255,.3);
  border-radius: var(--radius);
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  backdrop-filter: blur(8px);
  cursor: text;
  transition: border-color .15s;
}
.ai-search-bar:focus-within { border-color: rgba(255,255,255,.7); }
.ai-icon { font-size: 20px; flex-shrink: 0; }
.ai-search-bar input {
  background: none;
  border: none;
  outline: none;
  color: var(--white);
  font-size: 16px;
  font-family: var(--font);
  flex: 1;
}
.ai-search-bar input::placeholder { color: rgba(255,255,255,.6); }
.ai-badge {
  background: rgba(255,255,255,.2);
  color: var(--white);
  font-size: 11px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 4px;
  letter-spacing: .5px;
  flex-shrink: 0;
}
.ai-divider {
  text-align: center;
  color: rgba(255,255,255,.6);
  font-size: 13px;
  margin: 12px 0;
  position: relative;
}
.ai-divider::before, .ai-divider::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 38%;
  height: 1px;
  background: rgba(255,255,255,.25);
}
.ai-divider::before { left: 0; }
.ai-divider::after { right: 0; }

/* ===== SEARCH FORM ===== */
.search-form {
  background: var(--white);
  border-radius: var(--radius);
  padding: 24px;
  box-shadow: var(--shadow-lg);
}
.search-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 20px;
  border-bottom: 2px solid var(--gray-100);
  padding-bottom: 0;
}
.search-tab {
  padding: 8px 18px;
  border: none;
  background: none;
  font-weight: 600;
  font-size: 14px;
  color: var(--gray-400);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all .15s;
  font-family: var(--font);
}
.search-tab.active { color: var(--green); border-bottom-color: var(--green); }
.search-fields {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr auto;
  gap: 12px;
  align-items: end;
}
.search-field { position: relative; }
.search-field-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--gray-400);
  font-size: 16px;
  pointer-events: none;
}
.search-field .form-control { padding-left: 38px; }
.search-field-label {
  font-size: 11px;
  font-weight: 700;
  color: var(--gray-400);
  text-transform: uppercase;
  letter-spacing: .5px;
  margin-bottom: 5px;
}
.search-btn {
  padding: 13px 28px;
  background: var(--green);
  color: var(--white);
  border: none;
  border-radius: var(--radius-sm);
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  transition: background .15s;
  font-family: var(--font);
}
.search-btn:hover { background: var(--green-dark); }
@media (max-width: 900px) {
  .search-fields { grid-template-columns: 1fr 1fr; }
  .search-btn { grid-column: 1 / -1; }
}
@media (max-width: 480px) {
  .search-fields { grid-template-columns: 1fr; }
}

/* ===== RESULTS ===== */
.results-layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 24px;
  align-items: start;
}
@media (max-width: 860px) {
  .results-layout { grid-template-columns: 1fr; }
}

/* Filter Sidebar */
.filter-sidebar {
  background: var(--white);
  border-radius: var(--radius);
  border: 1px solid var(--gray-200);
  padding: 20px;
  position: sticky;
  top: 80px;
}
.filter-title {
  font-weight: 700;
  font-size: 15px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--gray-200);
}
.filter-group { margin-bottom: 20px; }
.filter-group-title { font-size: 12px; font-weight: 700; color: var(--gray-600); text-transform: uppercase; letter-spacing: .5px; margin-bottom: 10px; }
.filter-option { display: flex; align-items: center; gap: 8px; margin-bottom: 7px; cursor: pointer; font-size: 14px; }
.filter-option input[type=checkbox], .filter-option input[type=radio] { accent-color: var(--green); width: 15px; height: 15px; }
.filter-range { width: 100%; accent-color: var(--green); }
.filter-range-labels { display: flex; justify-content: space-between; font-size: 12px; color: var(--gray-400); margin-top: 4px; }

/* Flight Cards */
.flight-card {
  background: var(--white);
  border-radius: var(--radius);
  border: 1px solid var(--gray-200);
  margin-bottom: 14px;
  overflow: hidden;
  transition: box-shadow .18s, transform .18s;
}
.flight-card:hover { box-shadow: var(--shadow); transform: translateY(-1px); }
.flight-card.africa-direct { border-left: 4px solid var(--green); }
.flight-card-header {
  display: grid;
  grid-template-columns: 1fr auto 1fr auto;
  align-items: center;
  gap: 16px;
  padding: 20px 22px;
}
.flight-airline { display: flex; align-items: center; gap: 10px; }
.airline-logo {
  width: 38px; height: 38px;
  background: var(--green-pale);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  font-size: 13px;
  color: var(--green-dark);
  flex-shrink: 0;
}
.airline-name { font-weight: 600; font-size: 14px; }
.airline-flight { font-size: 12px; color: var(--gray-400); }

.flight-route {
  display: flex;
  align-items: center;
  gap: 12px;
  grid-column: 1 / -1;
  justify-content: center;
}
.flight-time { text-align: center; }
.flight-time-val { font-size: 1.4rem; font-weight: 800; }
.flight-time-code { font-size: 12px; color: var(--gray-400); font-weight: 600; }
.flight-line {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  max-width: 160px;
}
.flight-line-track {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 4px;
}
.line { flex: 1; height: 2px; background: var(--gray-200); }
.plane-icon { color: var(--green); font-size: 14px; }
.flight-duration { font-size: 12px; color: var(--gray-600); font-weight: 600; }
.flight-stops { font-size: 11px; color: var(--gray-400); }
.flight-stops.nonstop { color: var(--green); font-weight: 600; }

.flight-card-pricing {
  border-top: 1px solid var(--gray-100);
  padding: 14px 22px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}
.true-cost {
  flex: 1;
}
.true-cost-total { font-size: 1.5rem; font-weight: 900; color: var(--green); }
.true-cost-label { font-size: 11px; color: var(--gray-400); }
.true-cost-breakdown {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 6px;
}
.cost-item {
  font-size: 11px;
  color: var(--gray-600);
  background: var(--gray-100);
  padding: 2px 7px;
  border-radius: 4px;
}
.cost-item.highlight { background: var(--green-pale); color: var(--green-dark); font-weight: 600; }

.flight-card-actions { display: flex; flex-direction: column; gap: 8px; align-items: flex-end; }
.africa-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: var(--green-pale);
  color: var(--green-dark);
  font-size: 11px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 4px;
}

/* OTA Options */
.ota-options {
  border-top: 1px solid var(--gray-100);
  padding: 12px 22px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.ota-option {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--gray-50);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-sm);
  padding: 7px 12px;
  cursor: pointer;
  transition: all .15s;
  font-size: 13px;
}
.ota-option:hover { border-color: var(--green); background: var(--green-pale); }
.ota-option.best { border-color: var(--green); background: var(--green-pale); }
.ota-name { font-weight: 600; }
.ota-price { color: var(--green); font-weight: 700; }
.ota-verified { color: var(--green); font-size: 11px; }
.ota-unverified { color: var(--amber); font-size: 11px; }

/* Results header */
.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 10px;
}
.results-count { font-weight: 700; font-size: 15px; }
.results-sort { display: flex; align-items: center; gap: 8px; font-size: 14px; }
.results-sort select { padding: 6px 10px; border: 1px solid var(--gray-200); border-radius: var(--radius-sm); font-size: 14px; }

/* Price Hold */
.price-hold-btn {
  background: none;
  border: 1.5px solid var(--green);
  color: var(--green);
  border-radius: var(--radius-sm);
  padding: 5px 12px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  font-family: var(--font);
  transition: all .15s;
}
.price-hold-btn:hover { background: var(--green); color: var(--white); }

/* ===== MULTI-CITY ===== */
.mc-legs { display: flex; flex-direction: column; gap: 10px; margin-bottom: 14px; }
.mc-leg {
  display: grid;
  grid-template-columns: 1fr auto 1fr 160px auto;
  gap: 10px;
  align-items: end;
  background: var(--gray-50);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-sm);
  padding: 12px;
}
.mc-leg-num {
  grid-column: 1 / -1;
  font-size: 11px;
  font-weight: 700;
  color: var(--gray-400);
  text-transform: uppercase;
  letter-spacing: .5px;
  margin-bottom: 4px;
}
.mc-arrow { color: var(--green); font-weight: 700; font-size: 18px; padding-bottom: 10px; text-align: center; }
.mc-remove {
  background: none; border: 1px solid var(--gray-200); border-radius: var(--radius-sm);
  color: var(--gray-400); cursor: pointer; padding: 8px 10px; font-size: 14px;
  transition: all .15s; align-self: end; margin-bottom: 0;
}
.mc-remove:hover { border-color: var(--red); color: var(--red); }
.mc-add-leg {
  background: none; border: 1.5px dashed var(--green); color: var(--green);
  border-radius: var(--radius-sm); padding: 9px 18px; font-size: 14px; font-weight: 600;
  cursor: pointer; font-family: var(--font); transition: all .15s; width: 100%;
}
.mc-add-leg:hover { background: var(--green-pale); }
.mc-leg-summary {
  background: var(--green-pale);
  border: 1px solid var(--green);
  border-radius: var(--radius);
  padding: 12px 16px;
  margin-bottom: 12px;
  font-size: 13px;
  font-weight: 600;
  color: var(--green-dark);
}
@media (max-width: 700px) {
  .mc-leg { grid-template-columns: 1fr 1fr; }
  .mc-arrow { display: none; }
  .mc-remove { grid-column: 1 / -1; }
}

/* Multi-city results: leg panels */
.mc-leg-panel {
  background: var(--white);
  border-radius: var(--radius);
  border: 2px solid var(--gray-200);
  margin-bottom: 20px;
  overflow: hidden;
  transition: border-color .2s;
}
.mc-leg-panel.selected { border-color: var(--green); }
.mc-leg-panel-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 20px; background: var(--gray-50);
  border-bottom: 1px solid var(--gray-200);
}
.mc-leg-label { font-weight: 700; font-size: 15px; }
.mc-leg-route { font-size: 13px; color: var(--gray-600); margin-top: 2px; }
.mc-selected-badge { background: var(--green); color: white; font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 20px; }
.mc-leg-flights { padding: 12px; }
.mc-select-btn {
  background: var(--green-pale); border: 1.5px solid var(--green); color: var(--green-dark);
  border-radius: var(--radius-sm); padding: 6px 14px; font-size: 13px; font-weight: 700;
  cursor: pointer; font-family: var(--font); transition: all .15s; white-space: nowrap;
}
.mc-select-btn:hover, .mc-select-btn.active { background: var(--green); color: white; }
.mc-total-bar {
  background: var(--green-dark); color: white; border-radius: var(--radius);
  padding: 16px 24px; margin-bottom: 20px;
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;
}
.mc-total-label { font-size: 14px; opacity: .85; }
.mc-total-amount { font-size: 1.6rem; font-weight: 900; }
.mc-itinerary { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 700; flex-wrap: wrap; }
.mc-itinerary-arrow { color: rgba(255,255,255,.6); }

/* No results */
.no-results {
  text-align: center;
  padding: 60px 20px;
  color: var(--gray-400);
}
.no-results-icon { font-size: 48px; margin-bottom: 16px; }

```

## FILE: frontend/css/admin.css
```css
/* ===== ADMIN LAYOUT ===== */
.admin-body { display: flex; min-height: 100vh; background: var(--gray-100); }

.admin-sidebar {
  width: 240px;
  background: var(--gray-800);
  color: var(--white);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0; left: 0; bottom: 0;
  z-index: 200;
  transition: transform .25s;
}
.admin-sidebar-logo {
  padding: 20px 20px 16px;
  border-bottom: 1px solid #374151;
}
.admin-logo-text { font-size: 1.3rem; font-weight: 900; color: var(--green-light); }
.admin-logo-sub { font-size: 11px; color: #6b7280; margin-top: 2px; }
.admin-nav { flex: 1; padding: 12px 0; overflow-y: auto; }
.admin-nav-section { padding: 8px 16px 4px; font-size: 10px; font-weight: 700; color: #6b7280; text-transform: uppercase; letter-spacing: .8px; }
.admin-nav-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  color: #d1d5db;
  font-size: 14px;
  font-weight: 500;
  transition: all .15s;
  border-left: 3px solid transparent;
}
.admin-nav-link:hover { background: #374151; color: var(--white); text-decoration: none; }
.admin-nav-link.active { background: rgba(64,126,60,.2); color: var(--green-light); border-left-color: var(--green-light); }
.admin-nav-icon { font-size: 16px; width: 20px; text-align: center; flex-shrink: 0; }
.admin-sidebar-footer { padding: 16px; border-top: 1px solid #374151; }
.admin-user-info { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.admin-avatar-sm { width: 36px; height: 36px; border-radius: 50%; background: var(--green); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13px; color: var(--white); flex-shrink: 0; }
.admin-user-name { font-size: 13px; font-weight: 600; color: var(--white); }
.admin-user-role { font-size: 11px; color: #6b7280; }
.admin-logout-btn { display: flex; align-items: center; gap: 8px; color: #9ca3af; font-size: 13px; background: none; border: none; cursor: pointer; width: 100%; padding: 6px 0; font-family: var(--font); }
.admin-logout-btn:hover { color: var(--white); }

.admin-main { margin-left: 240px; flex: 1; display: flex; flex-direction: column; }
.admin-topbar {
  background: var(--white);
  border-bottom: 1px solid var(--gray-200);
  padding: 0 28px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: var(--shadow-sm);
}
.admin-page-title { font-size: 1.1rem; font-weight: 700; }
.admin-topbar-actions { display: flex; align-items: center; gap: 12px; }
.admin-content { padding: 28px; flex: 1; }

@media (max-width: 900px) {
  .admin-sidebar { transform: translateX(-100%); }
  .admin-sidebar.open { transform: translateX(0); }
  .admin-main { margin-left: 0; }
}

/* ===== STAT CARDS ===== */
.stat-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }
.stat-card { background: var(--white); border-radius: var(--radius); border: 1px solid var(--gray-200); padding: 20px; }
.stat-label { font-size: 12px; color: var(--gray-400); text-transform: uppercase; letter-spacing: .5px; font-weight: 700; margin-bottom: 8px; }
.stat-value { font-size: 1.8rem; font-weight: 900; color: var(--gray-800); }
.stat-sub { font-size: 12px; color: var(--gray-400); margin-top: 4px; }
.stat-icon { font-size: 1.6rem; float: right; margin-top: -4px; }
.stat-card.green { border-left: 4px solid var(--green); }
.stat-card.amber { border-left: 4px solid var(--amber); }
.stat-card.blue { border-left: 4px solid var(--blue); }
.stat-card.red { border-left: 4px solid var(--red); }

/* ===== TABLES ===== */
.table-card { background: var(--white); border-radius: var(--radius); border: 1px solid var(--gray-200); overflow: hidden; }
.table-card-header { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid var(--gray-200); }
.table-card-title { font-weight: 700; }
.table-wrapper { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
thead tr { background: var(--gray-50); }
th { padding: 11px 16px; text-align: left; font-size: 11px; font-weight: 700; color: var(--gray-400); text-transform: uppercase; letter-spacing: .5px; border-bottom: 1px solid var(--gray-200); white-space: nowrap; }
td { padding: 13px 16px; border-bottom: 1px solid var(--gray-100); color: var(--gray-800); vertical-align: middle; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: var(--gray-50); }
.td-mono { font-family: monospace; font-weight: 700; }

/* Pagination */
.pagination { display: flex; align-items: center; justify-content: center; gap: 6px; padding: 16px; border-top: 1px solid var(--gray-200); }
.page-btn { padding: 6px 12px; border: 1px solid var(--gray-200); border-radius: var(--radius-sm); background: var(--white); cursor: pointer; font-size: 14px; font-family: var(--font); transition: all .15s; }
.page-btn:hover { border-color: var(--green); color: var(--green); }
.page-btn.active { background: var(--green); color: var(--white); border-color: var(--green); }
.page-btn:disabled { opacity: .4; cursor: not-allowed; }

/* Search + Filter bar */
.table-toolbar { display: flex; align-items: center; gap: 10px; padding: 14px 20px; border-bottom: 1px solid var(--gray-200); flex-wrap: wrap; }
.toolbar-search { flex: 1; min-width: 200px; position: relative; }
.toolbar-search input { width: 100%; padding: 8px 12px 8px 36px; border: 1px solid var(--gray-200); border-radius: var(--radius-sm); font-size: 14px; font-family: var(--font); }
.toolbar-search-icon { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: var(--gray-400); }
.toolbar-select { padding: 8px 12px; border: 1px solid var(--gray-200); border-radius: var(--radius-sm); font-size: 14px; font-family: var(--font); }

/* Staff form modal */
.role-select { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.role-option { border: 2px solid var(--gray-200); border-radius: var(--radius-sm); padding: 10px 12px; cursor: pointer; transition: all .15s; }
.role-option input { display: none; }
.role-option:has(input:checked) { border-color: var(--green); background: var(--green-pale); }
.role-option-label { font-weight: 700; font-size: 13px; }
.role-option-desc { font-size: 11px; color: var(--gray-400); margin-top: 2px; }

/* Finance charts placeholder */
.chart-placeholder { background: var(--gray-50); border-radius: var(--radius); border: 1px dashed var(--gray-200); height: 200px; display: flex; align-items: center; justify-content: center; color: var(--gray-400); font-size: 14px; }

/* Revenue summary */
.revenue-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 14px; margin-bottom: 24px; }
.revenue-card { background: var(--white); border-radius: var(--radius); border: 1px solid var(--gray-200); padding: 16px; }
.revenue-label { font-size: 11px; color: var(--gray-400); text-transform: uppercase; letter-spacing: .5px; font-weight: 700; }
.revenue-value { font-size: 1.4rem; font-weight: 900; color: var(--green); margin-top: 4px; }

/* Mobile hamburger */
.admin-hamburger {
  display: none;
  flex-direction: column;
  justify-content: space-between;
  width: 28px; height: 20px;
  background: none; border: none; cursor: pointer; padding: 0; margin-right: 14px;
}
.admin-hamburger span {
  display: block; height: 2px; background: var(--gray-800); border-radius: 2px; transition: all .2s;
}
@media (max-width: 900px) {
  .admin-hamburger { display: flex; }
}

/* Overlay when sidebar open on mobile */
.admin-overlay {
  display: none;
  position: fixed; inset: 0; background: rgba(0,0,0,.4); z-index: 199;
}
.admin-overlay.visible { display: block; }

/* Force change password */
.force-change-wrapper {
  min-height: 100vh;
  background: var(--gray-800);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.force-change-card {
  background: var(--white);
  border-radius: var(--radius-lg);
  padding: 36px;
  max-width: 440px;
  width: 100%;
  box-shadow: var(--shadow-lg);
}
.force-change-icon { font-size: 2.5rem; text-align: center; margin-bottom: 16px; }

```

## FILE: frontend/js/api.js
```js
const API_BASE = '/api';

async function apiFetch(path, options = {}) {
  const token = localStorage.getItem('af_token');
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(API_BASE + path, { ...options, headers });
  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    // Staff password change required — redirect
    if (res.status === 403 && data.must_change_password) {
      window.location.href = '/admin/change-password.html';
      return null;
    }
    throw { status: res.status, message: data.error || 'Request failed', data };
  }
  return data;
}

const api = {
  get: (path) => apiFetch(path),
  post: (path, body) => apiFetch(path, { method: 'POST', body: JSON.stringify(body) }),
  put: (path, body) => apiFetch(path, { method: 'PUT', body: JSON.stringify(body) }),
  del: (path) => apiFetch(path, { method: 'DELETE' }),
};

window.api = api;

function escapeHtml(str) {
  if (str == null) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
window.escapeHtml = escapeHtml;

```

## FILE: frontend/js/auth.js
```js
const Auth = {
  TOKEN_KEY: 'af_token',
  USER_KEY: 'af_user',
  ROLE_KEY: 'af_role',

  save(token, user) {
    localStorage.setItem(this.TOKEN_KEY, token);
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    localStorage.setItem(this.ROLE_KEY, user.role || 'customer');
  },

  saveStaff(token, staff) {
    localStorage.setItem(this.TOKEN_KEY, token);
    localStorage.setItem(this.USER_KEY, JSON.stringify(staff));
    localStorage.setItem(this.ROLE_KEY, staff.role);
  },

  getToken() { return localStorage.getItem(this.TOKEN_KEY); },
  getUser() {
    try { return JSON.parse(localStorage.getItem(this.USER_KEY)); }
    catch { return null; }
  },
  getRole() { return localStorage.getItem(this.ROLE_KEY); },

  isLoggedIn() { return !!this.getToken(); },
  isStaff() { return ['super_admin','admin','agent','finance'].includes(this.getRole()); },
  isCustomer() { return this.getRole() === 'customer'; },

  logout() {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
    localStorage.removeItem(this.ROLE_KEY);
  },

  requireLogin(redirectTo = '/auth/login.html') {
    if (!this.isLoggedIn()) { window.location.href = redirectTo; return false; }
    return true;
  },

  requireStaff() {
    if (!this.isLoggedIn() || !this.isStaff()) {
      window.location.href = '/admin/login.html';
      return false;
    }
    return true;
  },

  requireRole(...roles) {
    if (!this.requireStaff()) return false;
    if (!roles.includes(this.getRole())) {
      alert('Access denied. Insufficient permissions.');
      history.back();
      return false;
    }
    return true;
  },

  redirectIfLoggedIn(to = '/account/dashboard.html') {
    if (this.isLoggedIn() && this.isCustomer()) window.location.href = to;
    if (this.isLoggedIn() && this.isStaff()) window.location.href = '/admin/dashboard.html';
  },
};

window.Auth = Auth;

// Update navbar state
document.addEventListener('DOMContentLoaded', () => {
  const user = Auth.getUser();
  const loginLinks = document.querySelectorAll('[data-auth-login]');
  const logoutLinks = document.querySelectorAll('[data-auth-logout]');
  const userNameEl = document.querySelectorAll('[data-auth-name]');

  if (Auth.isLoggedIn() && user) {
    loginLinks.forEach(el => el.classList.add('hidden'));
    logoutLinks.forEach(el => el.classList.remove('hidden'));
    userNameEl.forEach(el => el.textContent = user.first_name || user.email);
  } else {
    loginLinks.forEach(el => el.classList.remove('hidden'));
    logoutLinks.forEach(el => el.classList.add('hidden'));
  }

  logoutLinks.forEach(el => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      Auth.logout();
      window.location.href = '/';
    });
  });
});

```

## FILE: frontend/js/search.js
```js
// Flight search logic
const Search = {
  results: [],
  filteredResults: [],

  async searchFlights(params) {
    const qs = new URLSearchParams({
      origin: params.origin,
      destination: params.destination,
      departure_date: params.departure_date,
      passengers: params.passengers || 1,
      cabin: params.cabin || 'economy',
      ...(params.return_date ? { return_date: params.return_date } : {}),
    });
    return api.get(`/flights/search?${qs}`);
  },

  async aiSearch(query) {
    return api.post('/flights/search/ai', { query });
  },

  async loadFeatured() {
    return api.get('/flights/featured');
  },

  async loadAirports() {
    return api.get('/flights/airports');
  },

  formatDuration(hours) {
    const h = Math.floor(hours);
    const m = Math.round((hours - h) * 60);
    return m > 0 ? `${h}h ${m}m` : `${h}h`;
  },

  trustColor(score) {
    if (score >= 4.5) return 'trust-score-high';
    if (score >= 3.5) return 'trust-score-mid';
    return 'trust-score-low';
  },

  renderFlightCard(flight) {
    const p = flight.pricing;
    const isAfrica = flight.is_africa_route;

    const africaBadge = isAfrica
      ? `<span class="africa-badge">✈ Africa Direct</span>`
      : '';

    const breakdown = `
      <div class="true-cost-breakdown">
        <span class="cost-item">Base $${p.base_fare}</span>
        <span class="cost-item">Markup $${p.markup}</span>
        <span class="cost-item">Service $${p.service_fee}</span>
        ${p.baggage_fee > 0 ? `<span class="cost-item">Baggage $${p.baggage_fee}</span>` : ''}
        ${p.seat_fee > 0 ? `<span class="cost-item">Seat $${p.seat_fee}</span>` : ''}
      </div>
    `;

    const otaOptions = flight.ota_options.map((ota, i) => `
      <div class="ota-option ${i === 0 ? 'best' : ''}" onclick="selectOTA('${flight.id}', '${ota.ota_id}', ${ota.price})">
        <span class="ota-name">${ota.ota_name}</span>
        <span class="${ota.verified ? 'ota-verified' : 'ota-unverified'}">${ota.verified ? '✓' : '⚠'}</span>
        <div class="trust-score ${this.trustColor(ota.trust_score)}">★${ota.trust_score}</div>
        <span class="ota-price">$${ota.price.toFixed(2)}</span>
      </div>
    `).join('');

    return `
      <div class="flight-card ${isAfrica ? 'africa-direct' : ''}" data-flight-id="${flight.id}">
        <div class="flight-card-header">
          <div class="flight-airline">
            <div class="airline-logo">${flight.airline_code}</div>
            <div>
              <div class="airline-name">${flight.airline}</div>
              <div class="airline-flight">${flight.flight_number}</div>
            </div>
          </div>
          <div style="flex:1;display:flex;align-items:center;justify-content:center;gap:16px;padding:0 16px;">
            <div class="flight-time">
              <div class="flight-time-val">${flight.departure_time}</div>
              <div class="flight-time-code">${flight.origin}</div>
            </div>
            <div class="flight-line">
              <div class="flight-line-track">
                <div class="line"></div>
                <span class="plane-icon">✈</span>
                <div class="line"></div>
              </div>
              <div class="flight-duration">${this.formatDuration(flight.duration_hours)}</div>
              <div class="flight-stops ${flight.stops === 0 ? 'nonstop' : ''}">${flight.stops_label}</div>
            </div>
            <div class="flight-time">
              <div class="flight-time-val">${flight.arrival_time}</div>
              <div class="flight-time-code">${flight.destination}</div>
            </div>
          </div>
          <div style="text-align:right;">
            ${africaBadge}
            <div class="text-sm text-gray">${flight.available_seats} seats left</div>
          </div>
        </div>
        <div class="flight-card-pricing">
          <div class="true-cost">
            <div class="true-cost-label">Total True Cost — no surprises</div>
            <div class="true-cost-total">$${p.total.toFixed(2)}</div>
            ${breakdown}
          </div>
          <div class="flight-card-actions">
            <button class="btn btn-primary" onclick="bookFlight('${flight.id}')">Book Now</button>
            <button class="price-hold-btn" onclick="holdPrice('${flight.id}', ${p.total})">⏱ Hold Price 24h</button>
          </div>
        </div>
        <div class="ota-options">
          <span style="font-size:12px;font-weight:700;color:var(--gray-400);align-self:center;margin-right:6px;">Book via:</span>
          ${otaOptions}
        </div>
      </div>
    `;
  },

  renderFeaturedRoute(route) {
    return `
      <div class="route-card" onclick="quickSearch('${route.origin}','${route.destination}')">
        <div class="route-from">${route.origin} → ${route.destination}</div>
        <div class="route-to">${route.label}</div>
        <div class="route-airline">${route.airline}</div>
        <div class="route-price">
          <span class="route-price-from">from </span>$${route.price_from}
        </div>
      </div>
    `;
  },
};

window.Search = Search;

// Store current flight for booking
window.currentFlight = null;

function bookFlight(flightId) {
  const flight = Search.results.find(f => f.id === flightId);
  if (!flight) return;
  sessionStorage.setItem('af_flight', JSON.stringify(flight));
  window.location.href = '/booking.html';
}

function selectOTA(flightId, otaId, price) {
  const flight = Search.results.find(f => f.id === flightId);
  if (!flight) return;
  const ota = flight.ota_options.find(o => o.ota_id === otaId);
  flight._selectedOta = ota;
  sessionStorage.setItem('af_flight', JSON.stringify(flight));
  window.location.href = '/booking.html';
}

function holdPrice(flightId, price) {
  if (!Auth.isLoggedIn()) {
    sessionStorage.setItem('af_redirect_after_login', window.location.href);
    window.location.href = '/auth/login.html';
    return;
  }
  alert(`Price held for 24 hours at $${price.toFixed(2)}. A small hold fee of $5 will be charged. (Demo mode — no actual charge)`);
}

function quickSearch(origin, destination) {
  const today = new Date();
  today.setDate(today.getDate() + 14);
  const date = today.toISOString().split('T')[0];
  window.location.href = `/results.html?origin=${origin}&destination=${destination}&departure_date=${date}&passengers=1&cabin=economy`;
}

```

## FILE: frontend/js/admin.js
```js
// Admin panel shared logic
const Admin = {
  async loadDashboard() {
    return api.get('/admin/dashboard');
  },

  async loadCustomers(page = 1, search = '') {
    return api.get(`/admin/customers?page=${page}&search=${encodeURIComponent(search)}`);
  },

  async loadAllBookings(page = 1, status = '') {
    return api.get(`/admin/bookings?page=${page}&status=${status}`);
  },

  async loadStaff() {
    return api.get('/admin/staff');
  },

  async createStaff(data) {
    return api.post('/admin/staff', data);
  },

  async updateStaff(id, data) {
    return api.put(`/admin/staff/${id}`, data);
  },

  async resetStaffPassword(id) {
    return api.post(`/admin/staff/${id}/reset-password`, {});
  },

  async updateBooking(id, data) {
    return api.put(`/admin/bookings/${id}`, data);
  },

  async loadFinance() {
    return api.get('/admin/finance/summary');
  },

  formatCurrency(usd) {
    return `$${Number(usd).toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
  },

  statusBadge(status) {
    const map = {
      confirmed: 'badge-green',
      pending: 'badge-amber',
      cancelled: 'badge-red',
      refunded: 'badge-blue',
    };
    return `<span class="badge ${map[status] || 'badge-gray'}">${status}</span>`;
  },

  roleBadge(role) {
    const map = {
      super_admin: 'badge-red',
      admin: 'badge-blue',
      agent: 'badge-green',
      finance: 'badge-amber',
    };
    const label = role.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase());
    return `<span class="badge ${map[role] || 'badge-gray'}">${label}</span>`;
  },

  // Render sidebar active link
  setActiveLink(href) {
    document.querySelectorAll('.admin-nav-link').forEach(el => {
      el.classList.toggle('active', el.getAttribute('href') === href);
    });
  },

  // Setup sidebar with user info
  initSidebar() {
    const user = Auth.getUser();
    if (!user) return;
    const nameEl = document.getElementById('sidebar-name');
    const roleEl = document.getElementById('sidebar-role');
    const avatarEl = document.getElementById('sidebar-avatar');
    if (nameEl) nameEl.textContent = `${user.first_name} ${user.last_name}`;
    if (roleEl) roleEl.textContent = user.role.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase());
    if (avatarEl) avatarEl.textContent = (user.first_name?.[0] || '') + (user.last_name?.[0] || '');

    // Hide role-restricted nav items
    document.querySelectorAll('[data-role-only]').forEach(el => {
      const allowed = el.dataset.roleOnly.split(',').map(s => s.trim());
      if (!allowed.includes(user.role)) el.style.display = 'none';
    });
  },

  showToast(msg, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type}`;
    toast.style.cssText = 'position:fixed;top:80px;right:20px;z-index:9999;min-width:280px;box-shadow:var(--shadow)';
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
  },
};

window.Admin = Admin;

document.addEventListener('DOMContentLoaded', () => {
  // Guard: all admin pages require staff
  if (!Auth.requireStaff()) return;
  Admin.initSidebar();

  // Inject hamburger button into topbar for mobile
  const topbar = document.querySelector('.admin-topbar');
  if (topbar) {
    const hamburger = document.createElement('button');
    hamburger.className = 'admin-hamburger';
    hamburger.setAttribute('aria-label', 'Toggle menu');
    hamburger.innerHTML = '<span></span><span></span><span></span>';
    topbar.prepend(hamburger);

    const sidebar = document.querySelector('.admin-sidebar');
    const overlay = document.createElement('div');
    overlay.className = 'admin-overlay';
    document.body.appendChild(overlay);

    function toggleSidebar() {
      const open = sidebar.classList.toggle('open');
      overlay.classList.toggle('visible', open);
    }
    hamburger.addEventListener('click', toggleSidebar);
    overlay.addEventListener('click', toggleSidebar);
  }

  // Logout button
  document.querySelectorAll('[data-admin-logout]').forEach(btn => {
    btn.addEventListener('click', () => {
      Auth.logout();
      window.location.href = '/admin/login.html';
    });
  });
});

```

## FILE: frontend/index.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Airfinder — Fly Smart, Pay Fair</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/main.css">
<link rel="stylesheet" href="/css/search.css">
<link rel="stylesheet" href="/css/components.css">
</head>
<body>

<!-- NAVBAR -->
<nav class="navbar">
  <div class="navbar-inner">
    <a href="/" class="navbar-brand">✈ Airfinder</a>
    <div class="navbar-links">
      <a href="/" class="navbar-link">Home</a>
      <a href="/results.html" class="navbar-link">Search</a>
      <a href="#transparency" class="navbar-link">About</a>
      <a href="/auth/login.html" class="navbar-link" data-auth-login>Login</a>
      <a href="/auth/register.html" class="btn btn-primary btn-sm" data-auth-login>Sign Up</a>
      <a href="/account/dashboard.html" class="navbar-link hidden" data-auth-logout>My Trips</a>
      <a href="#" class="navbar-link hidden" data-auth-logout>Logout</a>
    </div>
  </div>
</nav>

<!-- HERO -->
<section class="hero">
  <div class="container hero-content">
    <div class="hero-eyebrow">
      🌍 Global with Africa Focus &nbsp;|&nbsp; 🤖 AI-Powered Search
    </div>
    <h1>Find Flights.<br><em>See Every Fee.</em><br>Book With Confidence.</h1>
    <p class="hero-sub">
      The only flight search that shows your <strong>true total cost</strong> — base fare, markup, baggage, seat fees — before you click. No bait-and-switch. Ever.
    </p>

    <div class="trust-bar">
      <div class="trust-item">✅ True Cost Engine</div>
      <div class="trust-item">🔒 Verified OTA Partners</div>
      <div class="trust-item">🌍 Africa Route Intelligence</div>
      <div class="trust-item">🤖 AI Smart Search</div>
    </div>

    <!-- AI Search Bar -->
    <div class="ai-search-bar" id="aiBar">
      <span class="ai-icon">🤖</span>
      <input type="text" id="aiInput" placeholder='Try: "cheap flight from Lagos to London next month"' autocomplete="off">
      <span class="ai-badge">AI</span>
      <button class="btn btn-primary btn-sm" id="aiSearchBtn">Search</button>
    </div>

    <div class="ai-divider">or search manually</div>

    <!-- Search Form -->
    <div class="search-form">
      <div class="search-tabs">
        <button class="search-tab active" data-tab="oneway">One Way</button>
        <button class="search-tab" data-tab="roundtrip">Round Trip</button>
        <button class="search-tab" data-tab="multicity">✈ Multi-city</button>
      </div>

      <!-- One-way / Round-trip panel -->
      <div id="panel-simple">
        <div class="search-fields">
          <div class="search-field">
            <div class="search-field-label">From</div>
            <span class="search-field-icon">✈</span>
            <input class="form-control" type="text" id="origin" placeholder="Lagos (LOS)" list="airports-list">
          </div>
          <div class="search-field">
            <div class="search-field-label">To</div>
            <span class="search-field-icon">📍</span>
            <input class="form-control" type="text" id="destination" placeholder="London (LHR)" list="airports-list">
          </div>
          <div class="search-field">
            <div class="search-field-label">Date</div>
            <span class="search-field-icon">📅</span>
            <input class="form-control" type="date" id="departure_date">
          </div>
          <div class="search-field">
            <div class="search-field-label">Passengers & Class</div>
            <span class="search-field-icon">👤</span>
            <select class="form-control" id="passengers_cabin">
              <option value="1|economy">1 Passenger — Economy</option>
              <option value="1|business">1 Passenger — Business</option>
              <option value="1|first">1 Passenger — First</option>
              <option value="2|economy">2 Passengers — Economy</option>
              <option value="2|business">2 Passengers — Business</option>
              <option value="3|economy">3 Passengers — Economy</option>
              <option value="4|economy">4 Passengers — Economy</option>
            </select>
          </div>
          <button class="search-btn" id="searchBtn">🔍 Search</button>
        </div>
        <div id="return-date-row" class="hidden" style="margin-top:12px;">
          <div class="search-field" style="max-width:280px;">
            <div class="search-field-label">Return Date</div>
            <span class="search-field-icon">📅</span>
            <input class="form-control" type="date" id="return_date">
          </div>
        </div>
      </div>

      <!-- Multi-city panel -->
      <div id="panel-multicity" class="hidden">
        <div class="mc-legs" id="mc-legs-container"></div>
        <button class="mc-add-leg" id="mc-add-leg-btn">+ Add Another Leg</button>
        <div style="display:grid;grid-template-columns:1fr auto;gap:12px;margin-top:14px;align-items:end;">
          <div class="search-field">
            <div class="search-field-label">Passengers & Class</div>
            <select class="form-control" id="mc-passengers-cabin">
              <option value="1|economy">1 Passenger — Economy</option>
              <option value="1|business">1 Passenger — Business</option>
              <option value="1|first">1 Passenger — First</option>
              <option value="2|economy">2 Passengers — Economy</option>
              <option value="2|business">2 Passengers — Business</option>
              <option value="3|economy">3 Passengers — Economy</option>
              <option value="4|economy">4 Passengers — Economy</option>
            </select>
          </div>
          <button class="search-btn" id="mc-search-btn">🔍 Search Flights</button>
        </div>
      </div>
    </div>
    <datalist id="airports-list"></datalist>
  </div>
</section>

<!-- FEATURED ROUTES -->
<section class="section">
  <div class="container">
    <h2 style="margin-bottom:8px;">✈ Popular Routes</h2>
    <p class="text-gray mb-3">Top picks for African travelers — best prices updated daily</p>
    <div class="featured-grid" id="featuredGrid">
      <div class="spinner" style="margin:20px auto;"></div>
    </div>
  </div>
</section>

<!-- TRANSPARENCY SECTION -->
<section class="section transparency-section" id="transparency">
  <div class="container">
    <div class="text-center">
      <h2>How Airfinder Earns — Full Transparency</h2>
      <p class="text-gray mt-2">We believe you deserve to know exactly how we make money. No hidden agenda.</p>
    </div>
    <div class="earn-grid">
      <div class="earn-card">
        <div class="earn-icon">💰</div>
        <div class="earn-label">Booking Commission</div>
        <div class="earn-desc">We earn a small commission from airlines and OTA partners when you complete a booking. This is industry-standard and already included in the fare shown.</div>
      </div>
      <div class="earn-card">
        <div class="earn-icon">📊</div>
        <div class="earn-label">Fare Markup</div>
        <div class="earn-desc">On some routes we buy wholesale fares and add a transparent markup. You'll always see this broken down in the True Cost panel before you pay.</div>
      </div>
      <div class="earn-card">
        <div class="earn-icon">🎫</div>
        <div class="earn-label">Service Fee</div>
        <div class="earn-desc">A flat service fee covers our technology and support. It's shown clearly in the price breakdown — never hidden in the total.</div>
      </div>
      <div class="earn-card">
        <div class="earn-icon">🏢</div>
        <div class="earn-label">B2B Licensing</div>
        <div class="earn-desc">Travel agencies can license the Airfinder platform to power their own search. This keeps Airfinder profitable without charging you more.</div>
      </div>
    </div>
  </div>
</section>

<!-- WHY AIRFINDER -->
<section class="section">
  <div class="container">
    <div class="text-center mb-4">
      <h2>Why Airfinder Beats the Rest</h2>
      <p class="text-gray mt-2">We built this after identifying every flaw in the top 5 flight search platforms.</p>
    </div>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px;">
      <div class="card card-body">
        <h4>🎯 True Cost Engine</h4>
        <p class="text-sm text-gray mt-1">Google Flights, Skyscanner, and Momondo hide baggage and seat fees until you're almost done. We show everything upfront.</p>
      </div>
      <div class="card card-body">
        <h4>🔒 OTA Trust Score</h4>
        <p class="text-sm text-gray mt-1">Skyscanner's biggest complaint: fraudulent OTAs. Every booking provider on Airfinder is verified and rated — you see the score before you click.</p>
      </div>
      <div class="card card-body">
        <h4>🤖 AI Smart Search</h4>
        <p class="text-sm text-gray mt-1">Type naturally: "business class Abuja to Dubai next month under ₦800k" — our AI understands you and finds the best matches instantly.</p>
      </div>
      <div class="card card-body">
        <h4>🌍 Africa Route Intelligence</h4>
        <p class="text-sm text-gray mt-1">African routes are underserved on global platforms. We prioritize direct African carrier flights and highlight connection savings.</p>
      </div>
      <div class="card card-body">
        <h4>👥 Group Booking Flow</h4>
        <p class="text-sm text-gray mt-1">No platform solves group travel. Airfinder lets multiple travelers add details, compare options together, and book in one flow.</p>
      </div>
      <div class="card card-body">
        <h4>⏱ 24-Hour Price Hold</h4>
        <p class="text-sm text-gray mt-1">See a great fare but not ready to commit? Lock it for 24 hours for a small fee — a feature only Hopper has, now on metasearch.</p>
      </div>
    </div>
  </div>
</section>

<!-- FOOTER -->
<footer class="footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <div class="footer-brand">✈ Airfinder</div>
        <p class="footer-tagline">Fly Smart, Pay Fair.<br>The flight search platform that hides nothing.</p>
      </div>
      <div>
        <div class="footer-title">Search</div>
        <ul class="footer-links">
          <li><a href="/results.html">Find Flights</a></li>
          <li><a href="/results.html">Cheap Deals</a></li>
          <li><a href="/#transparency">How We Earn</a></li>
        </ul>
      </div>
      <div>
        <div class="footer-title">Account</div>
        <ul class="footer-links">
          <li><a href="/auth/login.html">Login</a></li>
          <li><a href="/auth/register.html">Sign Up</a></li>
          <li><a href="/account/dashboard.html">My Trips</a></li>
        </ul>
      </div>
      <div>
        <div class="footer-title">Company</div>
        <ul class="footer-links">
          <li><a href="/#transparency">About</a></li>
          <li><a href="/admin/login.html">Staff Portal</a></li>
          <li><a href="mailto:support@airfinder.com">Support</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      © 2026 Airfinder. Built to compete — not to trick you.
    </div>
  </div>
</footer>

<script src="/js/api.js"></script>
<script src="/js/auth.js"></script>
<script src="/js/search.js"></script>
<script>
document.addEventListener('DOMContentLoaded', async () => {
  // Set default date (2 weeks from now)
  const d = new Date(); d.setDate(d.getDate() + 14);
  document.getElementById('departure_date').value = d.toISOString().split('T')[0];
  document.getElementById('departure_date').min = new Date().toISOString().split('T')[0];

  // Load airports datalist
  try {
    const airports = await Search.loadAirports();
    const dl = document.getElementById('airports-list');
    airports.forEach(a => {
      const opt = document.createElement('option');
      opt.value = `${a.city} (${a.code})`;
      dl.appendChild(opt);
    });
  } catch {}

  // Load featured routes
  try {
    const routes = await Search.loadFeatured();
    document.getElementById('featuredGrid').innerHTML = routes.map(r => Search.renderFeaturedRoute(r)).join('');
  } catch {
    document.getElementById('featuredGrid').innerHTML = '<p class="text-gray">Could not load featured routes.</p>';
  }

  // Tabs
  document.querySelectorAll('.search-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.search-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const t = tab.dataset.tab;
      document.getElementById('return-date-row').classList.toggle('hidden', t !== 'roundtrip');
      document.getElementById('panel-simple').classList.toggle('hidden', t === 'multicity');
      document.getElementById('panel-multicity').classList.toggle('hidden', t !== 'multicity');
    });
  });

  // Multi-city leg builder
  initMultiCity();

  // Manual search
  document.getElementById('searchBtn').addEventListener('click', doSearch);

  // AI search
  document.getElementById('aiSearchBtn').addEventListener('click', doAiSearch);
  document.getElementById('aiInput').addEventListener('keydown', e => { if (e.key === 'Enter') doAiSearch(); });
});

function extractIATA(str) {
  const m = str.match(/\(([A-Z]{3})\)/);
  return m ? m[1] : str.toUpperCase().slice(0, 3);
}

function doSearch() {
  const origin = extractIATA(document.getElementById('origin').value.trim());
  const destination = extractIATA(document.getElementById('destination').value.trim());
  const departure_date = document.getElementById('departure_date').value;
  const pc = document.getElementById('passengers_cabin').value.split('|');
  const return_date = document.getElementById('return_date').value;

  if (!origin || !destination || !departure_date) {
    alert('Please fill in From, To, and Date.');
    return;
  }

  const params = new URLSearchParams({ origin, destination, departure_date, passengers: pc[0], cabin: pc[1] });
  if (return_date) params.set('return_date', return_date);
  window.location.href = `/results.html?${params}`;
}

// ===== MULTI-CITY =====
let mcLegCount = 0;

function initMultiCity() {
  addMcLeg(); // start with 2 legs
  addMcLeg();
  document.getElementById('mc-add-leg-btn').addEventListener('click', () => {
    if (mcLegCount < 6) addMcLeg();
    else alert('Maximum 6 legs allowed.');
  });
  document.getElementById('mc-search-btn').addEventListener('click', doMultiCitySearch);
}

function addMcLeg() {
  mcLegCount++;
  const idx = mcLegCount;
  const today = new Date();
  today.setDate(today.getDate() + 14 + (idx - 1) * 3);
  const defaultDate = today.toISOString().split('T')[0];
  const min = new Date().toISOString().split('T')[0];

  const div = document.createElement('div');
  div.className = 'mc-leg';
  div.dataset.leg = idx;
  div.innerHTML = `
    <div class="mc-leg-num" style="grid-column:1/-1;">Leg ${idx}</div>
    <div class="search-field">
      <div class="search-field-label">From</div>
      <input class="form-control mc-origin" data-leg="${idx}" placeholder="City or IATA" list="airports-list">
    </div>
    <div class="mc-arrow">→</div>
    <div class="search-field">
      <div class="search-field-label">To</div>
      <input class="form-control mc-dest" data-leg="${idx}" placeholder="City or IATA" list="airports-list">
    </div>
    <div class="search-field">
      <div class="search-field-label">Date</div>
      <input class="form-control mc-date" data-leg="${idx}" type="date" value="${defaultDate}" min="${min}">
    </div>
    ${idx > 2 ? `<button class="mc-remove" onclick="removeMcLeg(this)" title="Remove leg">✕</button>` : '<div></div>'}
  `;
  document.getElementById('mc-legs-container').appendChild(div);
}

function removeMcLeg(btn) {
  btn.closest('.mc-leg').remove();
  mcLegCount--;
  // Re-number remaining legs
  document.querySelectorAll('.mc-leg').forEach((el, i) => {
    el.querySelector('.mc-leg-num').textContent = `Leg ${i + 1}`;
    el.dataset.leg = i + 1;
  });
}

function doMultiCitySearch() {
  const legs = [];
  let valid = true;
  document.querySelectorAll('.mc-leg').forEach((legEl, i) => {
    const origin = extractIATA(legEl.querySelector('.mc-origin').value.trim());
    const destination = extractIATA(legEl.querySelector('.mc-dest').value.trim());
    const date = legEl.querySelector('.mc-date').value;
    if (!origin || !destination || !date) { valid = false; }
    legs.push({ origin, destination, date });
  });

  if (!valid || legs.length < 2) {
    alert('Please fill in From, To, and Date for all legs.');
    return;
  }

  const pc = document.getElementById('mc-passengers-cabin').value.split('|');
  sessionStorage.setItem('af_mc_legs', JSON.stringify(legs));
  sessionStorage.setItem('af_mc_pax', JSON.stringify({ passengers: pc[0], cabin: pc[1] }));
  window.location.href = '/multicity.html';
}

async function doAiSearch() {
  const query = document.getElementById('aiInput').value.trim();
  if (!query) return;
  const btn = document.getElementById('aiSearchBtn');
  btn.textContent = '...'; btn.disabled = true;
  try {
    const data = await Search.aiSearch(query);
    if (data.parsed && data.parsed.origin && data.parsed.destination) {
      const p = data.parsed;
      const params = new URLSearchParams({
        origin: p.origin, destination: p.destination,
        departure_date: p.departure_date, passengers: p.passengers, cabin: p.cabin,
        ai_query: query,
      });
      window.location.href = `/results.html?${params}`;
    } else {
      alert("Couldn't parse that query. Try: 'flight from Lagos to London next month'");
    }
  } catch (e) {
    alert('Search failed. Please try again.');
  } finally {
    btn.textContent = 'Search'; btn.disabled = false;
  }
}
</script>
</body>
</html>

```

## FILE: frontend/results.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Flight Results — Airfinder</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/main.css">
<link rel="stylesheet" href="/css/search.css">
<link rel="stylesheet" href="/css/components.css">
</head>
<body>

<nav class="navbar">
  <div class="navbar-inner">
    <a href="/" class="navbar-brand">✈ Airfinder</a>
    <div class="navbar-links">
      <a href="/" class="navbar-link">← Back</a>
      <a href="/auth/login.html" class="navbar-link" data-auth-login>Login</a>
      <a href="/account/dashboard.html" class="navbar-link hidden" data-auth-logout>My Trips</a>
      <a href="#" class="navbar-link hidden" data-auth-logout>Logout</a>
    </div>
  </div>
</nav>

<!-- Mini search bar -->
<div style="background:var(--green);padding:12px 0;">
  <div class="container">
    <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
      <input class="form-control" id="sr-origin" placeholder="From" style="max-width:120px;">
      <span style="color:white;font-weight:700;">→</span>
      <input class="form-control" id="sr-destination" placeholder="To" style="max-width:120px;">
      <input class="form-control" id="sr-date" type="date" style="max-width:160px;">
      <select class="form-control" id="sr-passengers" style="max-width:180px;">
        <option value="1|economy">1 Pax — Economy</option>
        <option value="1|business">1 Pax — Business</option>
        <option value="2|economy">2 Pax — Economy</option>
        <option value="3|economy">3 Pax — Economy</option>
      </select>
      <button class="btn btn-secondary btn-sm" id="sr-search-btn">🔍 Update</button>
    </div>
    <div id="ai-query-info" class="hidden" style="color:rgba(255,255,255,.8);font-size:13px;margin-top:8px;"></div>
  </div>
</div>

<div class="container" style="padding-top:28px;padding-bottom:48px;">
  <div class="results-layout">
    <!-- Filter Sidebar -->
    <aside class="filter-sidebar">
      <div class="filter-title">🎛 Filters</div>

      <div class="filter-group">
        <div class="filter-group-title">Stops</div>
        <label class="filter-option"><input type="checkbox" class="filter-stops" value="0" checked> Nonstop</label>
        <label class="filter-option"><input type="checkbox" class="filter-stops" value="1" checked> 1 Stop</label>
        <label class="filter-option"><input type="checkbox" class="filter-stops" value="2" checked> 2+ Stops</label>
      </div>

      <div class="filter-group">
        <div class="filter-group-title">Max Price (USD)</div>
        <input type="range" class="filter-range" id="price-filter" min="50" max="3000" value="3000">
        <div class="filter-range-labels"><span>$50</span><span id="price-label">$3000</span></div>
      </div>

      <div class="filter-group">
        <div class="filter-group-title">Route Type</div>
        <label class="filter-option"><input type="checkbox" id="filter-africa" checked> 🌍 Africa Routes</label>
        <label class="filter-option"><input type="checkbox" id="filter-global" checked> 🌐 Global Routes</label>
      </div>

      <div class="filter-group">
        <div class="filter-group-title">OTA Trust</div>
        <label class="filter-option"><input type="checkbox" class="filter-ota" value="verified" checked> ✓ Verified only</label>
      </div>

      <button class="btn btn-secondary w-full" id="clear-filters">Clear Filters</button>
    </aside>

    <!-- Results Panel -->
    <main>
      <div class="results-header">
        <div class="results-count" id="results-count">Searching...</div>
        <div class="results-sort">
          Sort:
          <select id="sort-select">
            <option value="price">Lowest Price</option>
            <option value="duration">Shortest Duration</option>
            <option value="stops">Fewest Stops</option>
            <option value="trust">Highest Trust</option>
          </select>
        </div>
      </div>

      <div id="results-container">
        <div style="text-align:center;padding:60px 20px;">
          <div class="spinner"></div>
          <p class="text-gray mt-2">Finding the best flights...</p>
        </div>
      </div>
    </main>
  </div>
</div>

<script src="/js/api.js"></script>
<script src="/js/auth.js"></script>
<script src="/js/search.js"></script>
<script>
const params = new URLSearchParams(window.location.search);
const origin = params.get('origin') || '';
const destination = params.get('destination') || '';
const departure_date = params.get('departure_date') || '';
const passengers = params.get('passengers') || '1';
const cabin = params.get('cabin') || 'economy';
const return_date = params.get('return_date') || '';
const ai_query = params.get('ai_query') || '';

document.addEventListener('DOMContentLoaded', async () => {
  // Populate mini search
  document.getElementById('sr-origin').value = origin;
  document.getElementById('sr-destination').value = destination;
  document.getElementById('sr-date').value = departure_date;

  if (ai_query) {
    const info = document.getElementById('ai-query-info');
    info.classList.remove('hidden');
    info.textContent = `🤖 AI interpreted: "${ai_query}" → ${origin} → ${destination}`;
  }

  // Fetch results
  try {
    const data = await Search.searchFlights({ origin, destination, departure_date, passengers, cabin, return_date });
    Search.results = data.results || [];
    applyFilters();
  } catch (e) {
    document.getElementById('results-container').innerHTML = `
      <div class="no-results">
        <div class="no-results-icon">😔</div>
        <h3>No flights found</h3>
        <p class="text-gray mt-1">Try different dates or a different route.</p>
        <a href="/" class="btn btn-primary mt-3">New Search</a>
      </div>`;
    document.getElementById('results-count').textContent = 'No results';
  }

  // Sort
  document.getElementById('sort-select').addEventListener('change', applyFilters);

  // Filters
  document.querySelectorAll('.filter-stops, .filter-ota').forEach(el => el.addEventListener('change', applyFilters));
  document.getElementById('filter-africa').addEventListener('change', applyFilters);
  document.getElementById('filter-global').addEventListener('change', applyFilters);
  document.getElementById('price-filter').addEventListener('input', function() {
    document.getElementById('price-label').textContent = `$${this.value}`;
    applyFilters();
  });
  document.getElementById('clear-filters').addEventListener('click', clearFilters);

  // Mini search update
  document.getElementById('sr-search-btn').addEventListener('click', () => {
    const o = document.getElementById('sr-origin').value.trim().toUpperCase().slice(0,3);
    const d = document.getElementById('sr-destination').value.trim().toUpperCase().slice(0,3);
    const dt = document.getElementById('sr-date').value;
    const [pax, cb] = document.getElementById('sr-passengers').value.split('|');
    window.location.href = `/results.html?origin=${o}&destination=${d}&departure_date=${dt}&passengers=${pax}&cabin=${cb}`;
  });
});

function applyFilters() {
  let results = [...Search.results];

  // Stops filter
  const allowedStops = Array.from(document.querySelectorAll('.filter-stops:checked')).map(el => parseInt(el.value));
  results = results.filter(f => allowedStops.includes(Math.min(f.stops, 2)));

  // Price filter
  const maxPrice = parseFloat(document.getElementById('price-filter').value);
  results = results.filter(f => f.pricing.total <= maxPrice);

  // Route type
  const showAfrica = document.getElementById('filter-africa').checked;
  const showGlobal = document.getElementById('filter-global').checked;
  results = results.filter(f => (f.is_africa_route && showAfrica) || (!f.is_africa_route && showGlobal));

  // Sort
  const sort = document.getElementById('sort-select').value;
  if (sort === 'price') results.sort((a, b) => a.pricing.total - b.pricing.total);
  if (sort === 'duration') results.sort((a, b) => a.duration_hours - b.duration_hours);
  if (sort === 'stops') results.sort((a, b) => a.stops - b.stops);
  if (sort === 'trust') results.sort((a, b) => b.airline_trust_score - a.airline_trust_score);

  Search.filteredResults = results;
  renderResults(results);
}

function renderResults(results) {
  const count = results.length;
  document.getElementById('results-count').textContent =
    count > 0 ? `${count} flight${count !== 1 ? 's' : ''} found — ${origin} → ${destination}` : 'No flights match your filters';

  if (count === 0) {
    document.getElementById('results-container').innerHTML = `
      <div class="no-results">
        <div class="no-results-icon">🔍</div>
        <h3>No flights match your filters</h3>
        <p class="text-gray mt-1">Try relaxing your filters.</p>
      </div>`;
    return;
  }

  document.getElementById('results-container').innerHTML = results.map(f => Search.renderFlightCard(f)).join('');
}

function clearFilters() {
  document.querySelectorAll('.filter-stops').forEach(el => el.checked = true);
  document.getElementById('price-filter').value = 3000;
  document.getElementById('price-label').textContent = '$3000';
  document.getElementById('filter-africa').checked = true;
  document.getElementById('filter-global').checked = true;
  applyFilters();
}
</script>
</body>
</html>

```

## FILE: frontend/booking.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Book Flight — Airfinder</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/main.css">
<link rel="stylesheet" href="/css/components.css">
</head>
<body>

<nav class="navbar">
  <div class="navbar-inner">
    <a href="/" class="navbar-brand">✈ Airfinder</a>
    <div class="navbar-links">
      <a href="javascript:history.back()" class="navbar-link">← Back to Results</a>
    </div>
  </div>
</nav>

<div class="container" style="padding-top:32px;padding-bottom:60px;">
  <!-- Steps -->
  <div class="booking-steps">
    <div class="step active" id="step-1"><div class="step-num">1</div><div class="step-label">Passengers</div></div>
    <div class="step-connector"></div>
    <div class="step" id="step-2"><div class="step-num">2</div><div class="step-label">Add-ons</div></div>
    <div class="step-connector"></div>
    <div class="step" id="step-3"><div class="step-num">3</div><div class="step-label">Payment</div></div>
  </div>

  <div class="booking-layout">
    <!-- Left: Form -->
    <div>
      <div id="alert-container"></div>

      <!-- Flight Summary -->
      <div class="card card-body mb-3" id="flight-summary">
        <p class="text-gray">Loading flight details...</p>
      </div>

      <!-- Step 1: Passengers -->
      <div id="step-panel-1">
        <h3 class="mb-2">Passenger Details</h3>
        <div id="passengers-container"></div>
        <button class="btn btn-primary mt-3" id="next-to-addons">Continue to Add-ons →</button>
      </div>

      <!-- Step 2: Add-ons -->
      <div id="step-panel-2" class="hidden">
        <h3 class="mb-2">Select Add-ons</h3>
        <div class="card card-body mb-3">
          <h4 class="mb-2">🧳 Baggage</h4>
          <div style="display:flex;flex-direction:column;gap:8px;">
            <label class="filter-option"><input type="radio" name="baggage" value="carry_on" checked> Carry-on only — Free</label>
            <label class="filter-option"><input type="radio" name="baggage" value="checked_1"> 1 Checked bag — $35 per passenger</label>
            <label class="filter-option"><input type="radio" name="baggage" value="checked_2"> 2 Checked bags — $60 per passenger</label>
          </div>
        </div>
        <div class="card card-body mb-3">
          <h4 class="mb-2">💺 Seat Preference</h4>
          <div style="display:flex;flex-direction:column;gap:8px;">
            <label class="filter-option"><input type="radio" name="seat" value="standard" checked> Standard — Free</label>
            <label class="filter-option"><input type="radio" name="seat" value="window"> Window seat — $15 per passenger</label>
            <label class="filter-option"><input type="radio" name="seat" value="aisle"> Aisle seat — $10 per passenger</label>
            <label class="filter-option"><input type="radio" name="seat" value="extra_legroom"> Extra legroom — $45 per passenger</label>
            <label class="filter-option"><input type="radio" name="seat" value="front_row"> Front row — $30 per passenger</label>
          </div>
        </div>
        <div style="display:flex;gap:10px;">
          <button class="btn btn-secondary" onclick="goToStep(1)">← Back</button>
          <button class="btn btn-primary" id="next-to-payment">Continue to Payment →</button>
        </div>
      </div>

      <!-- Step 3: Payment -->
      <div id="step-panel-3" class="hidden">
        <h3 class="mb-2">Payment Details</h3>
        <div class="alert alert-info">🔒 Demo mode — no real payment processed. Click "Complete Booking" to confirm.</div>
        <div class="card card-body mb-3">
          <div class="form-group">
            <label class="form-label">Cardholder Name</label>
            <input class="form-control" id="card-name" placeholder="John Doe">
          </div>
          <div class="form-group card-input-group">
            <label class="form-label">Card Number</label>
            <input class="form-control" id="card-number" placeholder="4242 4242 4242 4242" maxlength="19">
            <div class="card-icons">
              <div class="card-icon">VISA</div>
              <div class="card-icon">MC</div>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Expiry</label>
              <input class="form-control" id="card-expiry" placeholder="MM/YY" maxlength="5">
            </div>
            <div class="form-group">
              <label class="form-label">CVV</label>
              <input class="form-control" id="card-cvv" placeholder="123" maxlength="4" type="password">
            </div>
          </div>
        </div>
        <div style="display:flex;gap:10px;">
          <button class="btn btn-secondary" onclick="goToStep(2)">← Back</button>
          <button class="btn btn-primary" id="complete-booking-btn" style="flex:1;">✅ Complete Booking</button>
        </div>
      </div>
    </div>

    <!-- Right: Price Summary -->
    <div>
      <div class="price-summary-card">
        <div class="price-summary-title">💰 Price Summary</div>
        <div id="price-breakdown">
          <p class="text-gray text-sm">Loading...</p>
        </div>
        <div class="price-transparency mt-2">
          🔍 <strong>Full transparency:</strong> Every charge is shown here. No fees added at checkout.
        </div>
      </div>
    </div>
  </div>
</div>

<script src="/js/api.js"></script>
<script src="/js/auth.js"></script>
<script>
let flight = null;
let passengerCount = 1;
let mcBooking = null; // multi-city booking data

document.addEventListener('DOMContentLoaded', () => {
  if (!Auth.requireLogin()) return;

  // Multi-city mode
  const rawMc = sessionStorage.getItem('af_mc_booking');
  if (rawMc) {
    mcBooking = JSON.parse(rawMc);
    passengerCount = mcBooking.passengers || 1;
    renderMcFlightSummary();
    renderPassengerForms();
    renderMcPriceSummary();
    document.getElementById('next-to-addons').addEventListener('click', validatePassengers);
    document.getElementById('next-to-payment').addEventListener('click', () => goToStep(3));
    document.getElementById('complete-booking-btn').addEventListener('click', completeMcBooking);
    document.querySelectorAll('input[name=baggage], input[name=seat]').forEach(el => {
      el.addEventListener('change', renderMcPriceSummary);
    });
    return;
  }

  const raw = sessionStorage.getItem('af_flight');
  if (!raw) { window.location.href = '/'; return; }
  flight = JSON.parse(raw);
  passengerCount = flight.passengers || 1;

  renderFlightSummary();
  renderPassengerForms();
  updatePriceSummary();

  // Add-on change listeners
  document.querySelectorAll('input[name=baggage], input[name=seat]').forEach(el => {
    el.addEventListener('change', updatePriceSummary);
  });

  document.getElementById('next-to-addons').addEventListener('click', validatePassengers);
  document.getElementById('next-to-payment').addEventListener('click', () => goToStep(3));
  document.getElementById('complete-booking-btn').addEventListener('click', completeBooking);

  // Card formatting
  document.getElementById('card-number').addEventListener('input', function() {
    this.value = this.value.replace(/\D/g, '').replace(/(\d{4})/g, '$1 ').trim().slice(0, 19);
  });
  document.getElementById('card-expiry').addEventListener('input', function() {
    this.value = this.value.replace(/\D/g, '').replace(/(\d{2})(\d)/, '$1/$2').slice(0, 5);
  });
});

function renderFlightSummary() {
  const p = flight.pricing;
  document.getElementById('flight-summary').innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;">
      <div>
        <div style="font-size:1.2rem;font-weight:800;">${flight.origin} → ${flight.destination}</div>
        <div class="text-gray text-sm">${flight.airline} · ${flight.flight_number} · ${flight.departure_date}</div>
        <div class="text-gray text-sm">${flight.departure_time} → ${flight.arrival_time} · ${flight.cabin}</div>
        ${flight.is_africa_route ? '<span class="badge badge-green mt-1">✈ Africa Direct</span>' : ''}
      </div>
      <div style="text-align:right;">
        <div style="font-size:1.4rem;font-weight:900;color:var(--green);">$${p.total.toFixed(2)}</div>
        <div class="text-gray text-sm">for ${passengerCount} passenger${passengerCount>1?'s':''}</div>
      </div>
    </div>`;
}

function renderPassengerForms() {
  const container = document.getElementById('passengers-container');
  container.innerHTML = '';
  for (let i = 0; i < passengerCount; i++) {
    container.innerHTML += `
      <div class="passenger-block">
        <div class="passenger-title">Passenger ${i+1}${i === 0 ? ' (Primary)' : ''}</div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">First Name</label>
            <input class="form-control pax-first" data-pax="${i}" placeholder="John" required>
          </div>
          <div class="form-group">
            <label class="form-label">Last Name</label>
            <input class="form-control pax-last" data-pax="${i}" placeholder="Doe" required>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Date of Birth</label>
            <input class="form-control pax-dob" data-pax="${i}" type="date" required>
          </div>
          <div class="form-group">
            <label class="form-label">Passport Number</label>
            <input class="form-control pax-passport" data-pax="${i}" placeholder="A1234567" required>
          </div>
        </div>
        ${i === 0 ? `
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Email</label>
            <input class="form-control pax-email" data-pax="0" type="email" placeholder="john@example.com">
          </div>
          <div class="form-group">
            <label class="form-label">Phone</label>
            <input class="form-control pax-phone" data-pax="0" placeholder="+234 800 000 0000">
          </div>
        </div>` : ''}
      </div>`;
  }
}

function validatePassengers() {
  const firsts = document.querySelectorAll('.pax-first');
  const lasts = document.querySelectorAll('.pax-last');
  for (let i = 0; i < passengerCount; i++) {
    if (!firsts[i].value.trim() || !lasts[i].value.trim()) {
      showAlert('Please fill in all passenger names.', 'error'); return;
    }
  }
  goToStep(2);
}

function goToStep(n) {
  [1,2,3].forEach(i => {
    document.getElementById(`step-panel-${i}`).classList.toggle('hidden', i !== n);
    const stepEl = document.getElementById(`step-${i}`);
    stepEl.classList.toggle('active', i === n);
    stepEl.classList.toggle('done', i < n);
  });
  updatePriceSummary();
  window.scrollTo(0, 0);
}

function getAddons() {
  const baggage = document.querySelector('input[name=baggage]:checked')?.value || 'carry_on';
  const seat = document.querySelector('input[name=seat]:checked')?.value || 'standard';
  return { baggage, seat };
}

async function updatePriceSummary() {
  const { baggage, seat } = getAddons();
  try {
    const pricing = await api.post('/flights/pricing/calculate', {
      base_fare: flight.pricing.base_fare,
      passengers: passengerCount,
      baggage, seat,
    });
    renderPriceBreakdown(pricing);
  } catch {
    renderPriceBreakdown(flight.pricing);
  }
}

function renderPriceBreakdown(p) {
  document.getElementById('price-breakdown').innerHTML = `
    <div class="price-line"><span>Base fare (×${p.passengers || passengerCount})</span><span>$${(p.base_fare * (p.passengers || passengerCount)).toFixed(2)}</span></div>
    <div class="price-line"><span>Markup (${p.markup_pct || 8}%)</span><span>$${(p.markup * (p.passengers || passengerCount)).toFixed(2)}</span></div>
    <div class="price-line"><span>Service fee</span><span>$${p.service_fee.toFixed(2)}</span></div>
    ${p.baggage_fee > 0 ? `<div class="price-line"><span>Baggage</span><span>$${p.baggage_fee.toFixed(2)}</span></div>` : ''}
    ${p.seat_fee > 0 ? `<div class="price-line"><span>Seat selection</span><span>$${p.seat_fee.toFixed(2)}</span></div>` : ''}
    <div class="price-line total"><span>Total</span><span style="color:var(--green);">$${p.total.toFixed(2)}</span></div>
    <div class="text-xs text-gray" style="margin-top:8px;">We earn: commission $${p.commission?.toFixed(2) || '—'} + service fee $${p.service_fee.toFixed(2)}</div>`;
}

function getPassengers() {
  const passengers = [];
  document.querySelectorAll('.pax-first').forEach((el, i) => {
    passengers.push({
      first_name: el.value.trim(),
      last_name: document.querySelectorAll('.pax-last')[i].value.trim(),
      dob: document.querySelectorAll('.pax-dob')[i].value,
      passport: document.querySelectorAll('.pax-passport')[i].value.trim(),
    });
  });
  return passengers;
}

async function completeBooking() {
  const btn = document.getElementById('complete-booking-btn');
  btn.disabled = true; btn.textContent = 'Processing...';

  const { baggage, seat } = getAddons();
  const pricingRes = await api.post('/flights/pricing/calculate', {
    base_fare: flight.pricing.base_fare, passengers: passengerCount, baggage, seat,
  });

  try {
    const result = await api.post('/bookings', {
      flight_id: flight.id,
      origin: flight.origin,
      destination: flight.destination,
      departure_date: flight.departure_date,
      airline: flight.airline,
      flight_number: flight.flight_number,
      cabin: flight.cabin,
      base_fare: flight.pricing.base_fare,
      passengers: getPassengers(),
      baggage, seat,
    });
    sessionStorage.setItem('af_booking', JSON.stringify(result.booking));
    sessionStorage.removeItem('af_flight');
    window.location.href = '/confirmation.html';
  } catch (e) {
    showAlert(e.message || 'Booking failed. Please try again.', 'error');
    btn.disabled = false; btn.textContent = '✅ Complete Booking';
  }
}

function showAlert(msg, type = 'error') {
  document.getElementById('alert-container').innerHTML =
    `<div class="alert alert-${type}">${msg}</div>`;
  window.scrollTo(0, 0);
}

// ===== MULTI-CITY FUNCTIONS =====
function renderMcFlightSummary() {
  const legs = mcBooking.legs;
  const route = legs.map((l, i) => `${l.origin}${i === legs.length - 1 ? ' → ' + l.destination : ''}`).join(' → ');
  document.getElementById('flight-summary').innerHTML = `
    <div style="margin-bottom:8px;">
      <span class="badge badge-blue">✈ Multi-city · ${legs.length} Legs</span>
    </div>
    ${legs.map((leg, i) => `
      <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;${i < legs.length - 1 ? 'border-bottom:1px solid var(--gray-100);' : ''}">
        <div>
          <div style="font-weight:700;">Leg ${i+1}: ${leg.origin} → ${leg.destination}</div>
          <div class="text-gray text-sm">${leg.airline} · ${leg.flight_number} · ${leg.date}</div>
          <div class="text-gray text-sm">${leg.departure_time} → ${leg.arrival_time} · ${leg.cabin}</div>
        </div>
        <div style="font-weight:700;color:var(--green);">$${leg.pricing.total.toFixed(2)}</div>
      </div>`).join('')}
    <div style="display:flex;justify-content:space-between;margin-top:10px;font-size:1.1rem;font-weight:900;">
      <span>Combined Total</span>
      <span style="color:var(--green);">$${mcBooking.combined_total.toFixed(2)}</span>
    </div>`;
}

function renderMcPriceSummary() {
  const baggage = document.querySelector('input[name=baggage]:checked')?.value || 'carry_on';
  const seat = document.querySelector('input[name=seat]:checked')?.value || 'standard';
  const BAGGAGE = { carry_on: 0, checked_1: 35, checked_2: 60 };
  const SEAT = { standard: 0, window: 15, aisle: 10, extra_legroom: 45, front_row: 30 };
  const baggageFee = (BAGGAGE[baggage] || 0) * passengerCount * mcBooking.legs.length;
  const seatFee = (SEAT[seat] || 0) * passengerCount * mcBooking.legs.length;
  const addons = baggageFee + seatFee;
  const grandTotal = mcBooking.combined_total + addons;

  document.getElementById('price-breakdown').innerHTML = `
    ${mcBooking.legs.map((leg, i) => `
      <div class="price-line text-sm">
        <span>Leg ${i+1}: ${leg.origin}→${leg.destination}</span>
        <span>$${leg.pricing.total.toFixed(2)}</span>
      </div>`).join('')}
    <hr class="divider">
    <div class="price-line"><span>Subtotal (${mcBooking.legs.length} legs)</span><span>$${mcBooking.combined_total.toFixed(2)}</span></div>
    ${baggageFee > 0 ? `<div class="price-line"><span>Baggage (all legs)</span><span>$${baggageFee.toFixed(2)}</span></div>` : ''}
    ${seatFee > 0 ? `<div class="price-line"><span>Seat selection (all legs)</span><span>$${seatFee.toFixed(2)}</span></div>` : ''}
    <div class="price-line total"><span>Grand Total</span><span style="color:var(--green);">$${grandTotal.toFixed(2)}</span></div>`;
}

async function completeMcBooking() {
  const btn = document.getElementById('complete-booking-btn');
  btn.disabled = true; btn.textContent = 'Processing...';

  const baggage = document.querySelector('input[name=baggage]:checked')?.value || 'carry_on';
  const seat = document.querySelector('input[name=seat]:checked')?.value || 'standard';

  try {
    const result = await api.post('/bookings/multicity', {
      legs: mcBooking.legs,
      passengers: getPassengers(),
      baggage, seat,
      cabin: mcBooking.cabin,
    });
    sessionStorage.setItem('af_booking', JSON.stringify({
      ...result.bookings[0],
      is_multicity: true,
      group_reference: result.group_reference,
      total_legs: result.total_legs,
      combined_total_usd: result.combined_total_usd,
    }));
    sessionStorage.removeItem('af_mc_booking');
    window.location.href = '/confirmation.html';
  } catch (e) {
    showAlert(e.message || 'Booking failed. Please try again.', 'error');
    btn.disabled = false; btn.textContent = '✅ Complete Booking';
  }
}
</script>
</body>
</html>

```

## FILE: frontend/multicity.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Multi-city Search — Airfinder</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/main.css">
<link rel="stylesheet" href="/css/search.css">
<link rel="stylesheet" href="/css/components.css">
</head>
<body>

<nav class="navbar">
  <div class="navbar-inner">
    <a href="/" class="navbar-brand">✈ Airfinder</a>
    <div class="navbar-links">
      <a href="/" class="navbar-link">← New Search</a>
      <a href="/auth/login.html" class="navbar-link" data-auth-login>Login</a>
      <a href="/account/dashboard.html" class="navbar-link hidden" data-auth-logout>My Trips</a>
      <a href="#" class="navbar-link hidden" data-auth-logout>Logout</a>
    </div>
  </div>
</nav>

<!-- Header bar -->
<div style="background:var(--green);padding:14px 0;">
  <div class="container">
    <div id="mc-itinerary-bar" class="mc-itinerary" style="color:white;">
      <span>Loading itinerary...</span>
    </div>
  </div>
</div>

<div class="container" style="padding-top:28px;padding-bottom:60px;">

  <!-- Total summary (sticky bottom feel via top position) -->
  <div id="mc-total-bar" class="mc-total-bar hidden">
    <div>
      <div class="mc-total-label" id="mc-total-label">Select a flight for each leg</div>
      <div class="mc-itinerary" id="mc-total-route" style="margin-top:4px;font-size:12px;opacity:.8;"></div>
    </div>
    <div style="display:flex;align-items:center;gap:16px;">
      <div>
        <div class="mc-total-label">Combined Total</div>
        <div class="mc-total-amount" id="mc-combined-total">$0.00</div>
      </div>
      <button class="btn btn-secondary" id="mc-book-btn" disabled onclick="proceedToBooking()">Book All Legs →</button>
    </div>
  </div>

  <!-- Leg panels -->
  <div id="mc-panels">
    <div style="text-align:center;padding:60px 20px;">
      <div class="spinner"></div>
      <p class="text-gray mt-2">Searching all legs...</p>
    </div>
  </div>

</div>

<script src="/js/api.js"></script>
<script src="/js/auth.js"></script>
<script src="/js/search.js"></script>
<script>
let mcLegs = [];       // raw leg params [{origin,destination,date}]
let mcPax = {};        // {passengers, cabin}
let legResults = [];   // [{leg_num, origin, destination, date, flights:[]}]
let selections = {};   // {legNum: flight}

document.addEventListener('DOMContentLoaded', async () => {
  const rawLegs = sessionStorage.getItem('af_mc_legs');
  const rawPax = sessionStorage.getItem('af_mc_pax');
  if (!rawLegs || !rawPax) { window.location.href = '/'; return; }

  mcLegs = JSON.parse(rawLegs);
  mcPax = JSON.parse(rawPax);

  // Render itinerary header
  const itinParts = mcLegs.map((l, i) => {
    const arrow = i < mcLegs.length - 1 ? '<span class="mc-itinerary-arrow">→</span>' : '';
    return `<strong>${l.origin}</strong>${arrow}`;
  });
  itinParts.push(`<strong>${mcLegs[mcLegs.length - 1].destination}</strong>`);
  document.getElementById('mc-itinerary-bar').innerHTML = '✈ ' + itinParts.join(' ');

  // Show total bar placeholder
  document.getElementById('mc-total-bar').classList.remove('hidden');
  updateTotalBar();

  // Search all legs
  try {
    const data = await api.post('/flights/search/multicity', {
      legs: mcLegs,
      passengers: parseInt(mcPax.passengers),
      cabin: mcPax.cabin,
    });
    legResults = data.legs;
    renderLegPanels();
  } catch (e) {
    document.getElementById('mc-panels').innerHTML = `
      <div class="no-results">
        <div class="no-results-icon">😔</div>
        <h3>Search failed</h3>
        <p class="text-gray mt-1">${e.message || 'Could not search flights. Please try again.'}</p>
        <a href="/" class="btn btn-primary mt-3">← New Search</a>
      </div>`;
  }
});

function renderLegPanels() {
  if (!legResults.length) {
    document.getElementById('mc-panels').innerHTML = '<p class="text-gray">No results.</p>';
    return;
  }

  document.getElementById('mc-panels').innerHTML = legResults.map(leg => `
    <div class="mc-leg-panel" id="leg-panel-${leg.leg_num}">
      <div class="mc-leg-panel-header">
        <div>
          <div class="mc-leg-label">Leg ${leg.leg_num} of ${legResults.length}</div>
          <div class="mc-leg-route">${leg.origin} → ${leg.destination} &nbsp;·&nbsp; ${leg.date} &nbsp;·&nbsp; ${leg.flights.length} option${leg.flights.length !== 1 ? 's' : ''}</div>
        </div>
        <div id="leg-badge-${leg.leg_num}"></div>
      </div>
      <div class="mc-leg-flights" id="leg-flights-${leg.leg_num}">
        ${leg.flights.length === 0
          ? '<p class="text-gray" style="padding:12px;">No flights found for this leg. Try different dates.</p>'
          : leg.flights.map(f => renderMcFlightCard(f, leg.leg_num)).join('')
        }
      </div>
    </div>
  `).join('');
}

function renderMcFlightCard(flight, legNum) {
  const p = flight.pricing;
  const isAfrica = flight.is_africa_route;
  return `
    <div class="flight-card ${isAfrica ? 'africa-direct' : ''}" id="mc-card-${legNum}-${flight.id}" style="margin-bottom:10px;">
      <div class="flight-card-header">
        <div class="flight-airline">
          <div class="airline-logo">${flight.airline_code}</div>
          <div>
            <div class="airline-name">${flight.airline}</div>
            <div class="airline-flight">${flight.flight_number}</div>
          </div>
        </div>
        <div style="flex:1;display:flex;align-items:center;justify-content:center;gap:16px;padding:0 16px;">
          <div class="flight-time">
            <div class="flight-time-val">${flight.departure_time}</div>
            <div class="flight-time-code">${flight.origin}</div>
          </div>
          <div class="flight-line">
            <div class="flight-line-track"><div class="line"></div><span class="plane-icon">✈</span><div class="line"></div></div>
            <div class="flight-duration">${Search.formatDuration(flight.duration_hours)}</div>
            <div class="flight-stops ${flight.stops === 0 ? 'nonstop' : ''}">${flight.stops_label}</div>
          </div>
          <div class="flight-time">
            <div class="flight-time-val">${flight.arrival_time}</div>
            <div class="flight-time-code">${flight.destination}</div>
          </div>
        </div>
        <div style="text-align:right;">
          ${isAfrica ? '<span class="africa-badge">✈ Africa Direct</span>' : ''}
          <div class="text-sm text-gray">${flight.available_seats} seats</div>
        </div>
      </div>
      <div class="flight-card-pricing">
        <div class="true-cost">
          <div class="true-cost-label">Leg price — True Cost</div>
          <div class="true-cost-total">$${p.total.toFixed(2)}</div>
          <div class="true-cost-breakdown">
            <span class="cost-item">Base $${p.base_fare}</span>
            <span class="cost-item">Markup $${p.markup}</span>
            <span class="cost-item">Fee $${p.service_fee}</span>
          </div>
        </div>
        <div class="flight-card-actions">
          <button class="mc-select-btn" id="mc-sel-${legNum}-${flight.id}"
            onclick="selectLegFlight(${legNum}, '${flight.id}')">
            Select This Flight
          </button>
        </div>
      </div>
    </div>`;
}

function selectLegFlight(legNum, flightId) {
  const leg = legResults.find(l => l.leg_num === legNum);
  const flight = leg.flights.find(f => f.id === flightId);
  selections[legNum] = flight;

  // Update button states for this leg
  leg.flights.forEach(f => {
    const btn = document.getElementById(`mc-sel-${legNum}-${f.id}`);
    if (btn) btn.classList.toggle('active', f.id === flightId);
  });

  // Mark panel as selected
  document.getElementById(`leg-panel-${legNum}`).classList.add('selected');
  document.getElementById(`leg-badge-${legNum}`).innerHTML =
    `<span class="mc-selected-badge">✓ Selected · $${flight.pricing.total.toFixed(2)}</span>`;

  updateTotalBar();
}

function updateTotalBar() {
  const totalLegs = legResults.length || mcLegs.length;
  const selectedCount = Object.keys(selections).length;
  const combinedTotal = Object.values(selections).reduce((s, f) => s + f.pricing.total, 0);

  document.getElementById('mc-combined-total').textContent = `$${combinedTotal.toFixed(2)}`;
  document.getElementById('mc-total-label').textContent =
    selectedCount === totalLegs
      ? `All ${totalLegs} legs selected — ready to book!`
      : `${selectedCount} of ${totalLegs} legs selected`;

  const allSelected = selectedCount === totalLegs && totalLegs > 0;
  document.getElementById('mc-book-btn').disabled = !allSelected;
}

function proceedToBooking() {
  const legs = legResults.map(leg => {
    const flight = selections[leg.leg_num];
    return {
      leg_num: leg.leg_num,
      flight_id: flight.id,
      origin: flight.origin,
      destination: flight.destination,
      date: leg.date,
      airline: flight.airline,
      flight_number: flight.flight_number,
      base_fare: flight.pricing.base_fare,
      pricing: flight.pricing,
      departure_time: flight.departure_time,
      arrival_time: flight.arrival_time,
      cabin: mcPax.cabin,
    };
  });

  sessionStorage.setItem('af_mc_booking', JSON.stringify({
    legs,
    passengers: parseInt(mcPax.passengers),
    cabin: mcPax.cabin,
    combined_total: Object.values(selections).reduce((s, f) => s + f.pricing.total, 0),
  }));
  sessionStorage.removeItem('af_mc_legs');
  sessionStorage.removeItem('af_mc_pax');
  window.location.href = '/booking.html';
}
</script>
</body>
</html>

```

## FILE: frontend/confirmation.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Booking Confirmed — Airfinder</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/main.css">
<link rel="stylesheet" href="/css/components.css">
</head>
<body>
<nav class="navbar">
  <div class="navbar-inner">
    <a href="/" class="navbar-brand">✈ Airfinder</a>
  </div>
</nav>
<div class="container" style="padding:60px 20px;max-width:580px;">
  <div style="text-align:center;">
    <div class="confirmation-icon">✓</div>
    <h1 style="margin-bottom:8px;">Booking Confirmed!</h1>
    <p class="text-gray">A confirmation has been sent to your email.</p>
  </div>
  <div class="card card-body mt-4" id="booking-details">
    <p class="text-gray">Loading...</p>
  </div>
  <div style="display:flex;gap:12px;margin-top:24px;justify-content:center;flex-wrap:wrap;">
    <a href="/account/bookings.html" class="btn btn-primary">View My Bookings</a>
    <a href="/" class="btn btn-secondary">Book Another Flight</a>
  </div>
</div>
<script src="/js/api.js"></script>
<script src="/js/auth.js"></script>
<script>
document.addEventListener('DOMContentLoaded', () => {
  const raw = sessionStorage.getItem('af_booking');
  if (!raw) { window.location.href = '/'; return; }
  const b = JSON.parse(raw);
  const p = b.pricing;
  document.getElementById('booking-details').innerHTML = `
    <div style="display:flex;justify-content:space-between;margin-bottom:16px;flex-wrap:wrap;gap:8px;">
      <div>
        <div style="font-size:1.2rem;font-weight:800;">${b.origin} → ${b.destination}</div>
        <div class="text-gray text-sm">${b.airline} · ${b.flight_number || ''} · ${b.departure_date}</div>
      </div>
      <span class="badge badge-green" style="height:fit-content;">Confirmed</span>
    </div>
    <div class="price-line"><span>Reference</span><span class="td-mono">${b.reference}</span></div>
    <div class="price-line"><span>Cabin</span><span>${b.cabin_class}</span></div>
    <div class="price-line"><span>Passengers</span><span>${b.passenger_count}</span></div>
    <hr class="divider">
    <div class="price-line"><span>Base fare</span><span>$${p.base_fare?.toFixed(2)}</span></div>
    <div class="price-line"><span>Markup</span><span>$${p.markup?.toFixed(2)}</span></div>
    <div class="price-line"><span>Service fee</span><span>$${p.service_fee?.toFixed(2)}</span></div>
    ${p.baggage_fee > 0 ? `<div class="price-line"><span>Baggage</span><span>$${p.baggage_fee?.toFixed(2)}</span></div>` : ''}
    <div class="price-line total"><span>Total Paid</span><span style="color:var(--green);">$${p.total?.toFixed(2)}</span></div>`;
});
</script>
</body>
</html>

```

## FILE: frontend/auth/login.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Login — Airfinder</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/main.css">
<link rel="stylesheet" href="/css/components.css">
</head>
<body>
<div class="auth-page">
  <div class="auth-card">
    <div class="auth-logo">
      <a href="/" class="auth-logo-text">✈ Airfinder</a>
      <div class="auth-logo-sub">Fly Smart, Pay Fair</div>
    </div>
    <h2 class="auth-title">Welcome back</h2>
    <p class="auth-sub">Sign in to access your bookings</p>

    <div id="alert"></div>

    <form id="login-form">
      <div class="form-group">
        <label class="form-label">Email</label>
        <input class="form-control" id="email" type="email" placeholder="you@example.com" required autocomplete="email">
      </div>
      <div class="form-group">
        <label class="form-label">Password</label>
        <div class="password-toggle">
          <input class="form-control" id="password" type="password" placeholder="Your password" required autocomplete="current-password">
          <button type="button" class="toggle-btn" id="toggle-pw">👁</button>
        </div>
      </div>
      <div style="text-align:right;margin-bottom:16px;">
        <a href="/auth/forgot-password.html" class="text-sm">Forgot password?</a>
      </div>
      <button class="btn btn-primary btn-full" type="submit" id="submit-btn">Sign In</button>
    </form>

    <div class="auth-footer">
      Don't have an account? <a href="/auth/register.html">Sign up free</a>
    </div>
    <div class="auth-footer" style="margin-top:8px;">
      <a href="/admin/login.html" class="text-sm text-gray">Staff portal →</a>
    </div>
  </div>
</div>
<script src="/js/api.js"></script>
<script src="/js/auth.js"></script>
<script>
document.addEventListener('DOMContentLoaded', () => {
  Auth.redirectIfLoggedIn();

  document.getElementById('toggle-pw').addEventListener('click', () => {
    const pw = document.getElementById('password');
    pw.type = pw.type === 'password' ? 'text' : 'password';
  });

  document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('submit-btn');
    btn.disabled = true; btn.textContent = 'Signing in...';
    clearAlert();
    try {
      const data = await api.post('/auth/login', {
        email: document.getElementById('email').value,
        password: document.getElementById('password').value,
      });
      Auth.save(data.token, { ...data.user, role: 'customer' });
      const redirect = sessionStorage.getItem('af_redirect_after_login') || '/account/dashboard.html';
      sessionStorage.removeItem('af_redirect_after_login');
      window.location.href = redirect;
    } catch (e) {
      showAlert(e.message || 'Login failed');
      btn.disabled = false; btn.textContent = 'Sign In';
    }
  });
});
function showAlert(msg) { document.getElementById('alert').innerHTML = `<div class="alert alert-error">${msg}</div>`; }
function clearAlert() { document.getElementById('alert').innerHTML = ''; }
</script>
</body>
</html>

```

## FILE: frontend/auth/register.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Create Account — Airfinder</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/main.css">
<link rel="stylesheet" href="/css/components.css">
</head>
<body>
<div class="auth-page">
  <div class="auth-card">
    <div class="auth-logo">
      <a href="/" class="auth-logo-text">✈ Airfinder</a>
      <div class="auth-logo-sub">Fly Smart, Pay Fair</div>
    </div>
    <h2 class="auth-title">Create your account</h2>
    <p class="auth-sub">Start booking flights with full price transparency</p>

    <div id="alert"></div>

    <form id="register-form">
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">First Name</label>
          <input class="form-control" id="first_name" placeholder="John" required>
        </div>
        <div class="form-group">
          <label class="form-label">Last Name</label>
          <input class="form-control" id="last_name" placeholder="Doe" required>
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Email</label>
        <input class="form-control" id="email" type="email" placeholder="you@example.com" required>
      </div>
      <div class="form-group">
        <label class="form-label">Phone (optional)</label>
        <input class="form-control" id="phone" placeholder="+234 800 000 0000" type="tel">
      </div>
      <div class="form-group">
        <label class="form-label">Password</label>
        <div class="password-toggle">
          <input class="form-control" id="password" type="password" placeholder="Min 8 characters" required>
          <button type="button" class="toggle-btn" id="toggle-pw">👁</button>
        </div>
        <div class="strength-bar mt-1"><div class="strength-fill" id="strength-fill" style="width:0;background:var(--red);"></div></div>
        <div class="text-xs text-gray mt-1" id="strength-label"></div>
      </div>
      <button class="btn btn-primary btn-full mt-2" type="submit" id="submit-btn">Create Account</button>
    </form>

    <div class="auth-footer mt-2">
      Already have an account? <a href="/auth/login.html">Sign in</a>
    </div>
  </div>
</div>
<script src="/js/api.js"></script>
<script src="/js/auth.js"></script>
<script>
document.addEventListener('DOMContentLoaded', () => {
  Auth.redirectIfLoggedIn();

  document.getElementById('toggle-pw').addEventListener('click', () => {
    const pw = document.getElementById('password');
    pw.type = pw.type === 'password' ? 'text' : 'password';
  });

  document.getElementById('password').addEventListener('input', function() {
    const v = this.value;
    let score = 0;
    if (v.length >= 8) score++;
    if (/[A-Z]/.test(v)) score++;
    if (/[0-9]/.test(v)) score++;
    if (/[^A-Za-z0-9]/.test(v)) score++;
    const labels = ['', 'Weak', 'Fair', 'Good', 'Strong'];
    const colors = ['', 'var(--red)', 'var(--amber)', 'var(--green-light)', 'var(--green)'];
    document.getElementById('strength-fill').style.width = `${score * 25}%`;
    document.getElementById('strength-fill').style.background = colors[score];
    document.getElementById('strength-label').textContent = labels[score];
  });

  document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('submit-btn');
    btn.disabled = true; btn.textContent = 'Creating account...';
    clearAlert();
    try {
      const data = await api.post('/auth/register', {
        email: document.getElementById('email').value,
        password: document.getElementById('password').value,
        first_name: document.getElementById('first_name').value,
        last_name: document.getElementById('last_name').value,
        phone: document.getElementById('phone').value,
      });
      Auth.save(data.token, { ...data.user, role: 'customer' });
      window.location.href = '/account/dashboard.html';
    } catch (e) {
      showAlert(e.message || 'Registration failed');
      btn.disabled = false; btn.textContent = 'Create Account';
    }
  });
});
function showAlert(msg) { document.getElementById('alert').innerHTML = `<div class="alert alert-error">${msg}</div>`; }
function clearAlert() { document.getElementById('alert').innerHTML = ''; }
</script>
</body>
</html>

```

## FILE: frontend/auth/forgot-password.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Forgot Password — Airfinder</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/main.css">
<link rel="stylesheet" href="/css/components.css">
</head>
<body>
<div class="auth-page">
  <div class="auth-card">
    <div class="auth-logo">
      <a href="/" class="auth-logo-text">✈ Airfinder</a>
    </div>
    <h2 class="auth-title">Forgot password?</h2>
    <p class="auth-sub">Enter your email and we'll send a reset link.</p>
    <div id="alert"></div>
    <form id="forgot-form">
      <div class="form-group">
        <label class="form-label">Email</label>
        <input class="form-control" id="email" type="email" placeholder="you@example.com" required>
      </div>
      <button class="btn btn-primary btn-full" type="submit" id="submit-btn">Send Reset Link</button>
    </form>
    <div class="auth-footer mt-2"><a href="/auth/login.html">← Back to login</a></div>
  </div>
</div>
<script src="/js/api.js"></script>
<script>
document.getElementById('forgot-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = document.getElementById('submit-btn');
  btn.disabled = true; btn.textContent = 'Sending...';
  try {
    await api.post('/auth/forgot-password', { email: document.getElementById('email').value });
    document.getElementById('alert').innerHTML = '<div class="alert alert-success">✓ If that email exists, a reset link has been sent. Check your inbox.</div>';
    document.getElementById('forgot-form').classList.add('hidden');
  } catch {
    document.getElementById('alert').innerHTML = '<div class="alert alert-error">Something went wrong. Try again.</div>';
    btn.disabled = false; btn.textContent = 'Send Reset Link';
  }
});
</script>
</body>
</html>

```

## FILE: frontend/auth/reset-password.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Reset Password — Airfinder</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/main.css">
<link rel="stylesheet" href="/css/components.css">
</head>
<body>
<div class="auth-page">
  <div class="auth-card">
    <div class="auth-logo">
      <a href="/" class="auth-logo-text">✈ Airfinder</a>
    </div>
    <h2 class="auth-title">Set new password</h2>
    <p class="auth-sub">Choose a strong password for your account.</p>
    <div id="alert"></div>
    <form id="reset-form">
      <div class="form-group">
        <label class="form-label">New Password</label>
        <div class="password-toggle">
          <input class="form-control" id="password" type="password" placeholder="Min 8 characters" required>
          <button type="button" class="toggle-btn" id="toggle-pw">👁</button>
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Confirm Password</label>
        <input class="form-control" id="confirm" type="password" placeholder="Repeat password" required>
      </div>
      <button class="btn btn-primary btn-full" type="submit" id="submit-btn">Reset Password</button>
    </form>
    <div class="auth-footer mt-2"><a href="/auth/login.html">← Back to login</a></div>
  </div>
</div>
<script src="/js/api.js"></script>
<script>
const token = new URLSearchParams(window.location.search).get('token');
if (!token) { document.getElementById('alert').innerHTML = '<div class="alert alert-error">Invalid or missing reset token.</div>'; }

document.getElementById('toggle-pw').addEventListener('click', () => {
  const pw = document.getElementById('password');
  pw.type = pw.type === 'password' ? 'text' : 'password';
});

document.getElementById('reset-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const pw = document.getElementById('password').value;
  const confirm = document.getElementById('confirm').value;
  if (pw !== confirm) { document.getElementById('alert').innerHTML = '<div class="alert alert-error">Passwords do not match.</div>'; return; }

  const btn = document.getElementById('submit-btn');
  btn.disabled = true; btn.textContent = 'Resetting...';
  try {
    await api.post('/auth/reset-password', { token, password: pw });
    document.getElementById('alert').innerHTML = '<div class="alert alert-success">✓ Password reset! Redirecting to login...</div>';
    document.getElementById('reset-form').classList.add('hidden');
    setTimeout(() => { window.location.href = '/auth/login.html'; }, 2000);
  } catch (e) {
    document.getElementById('alert').innerHTML = `<div class="alert alert-error">${e.message || 'Reset failed.'}</div>`;
    btn.disabled = false; btn.textContent = 'Reset Password';
  }
});
</script>
</body>
</html>

```

## FILE: frontend/account/dashboard.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>My Account — Airfinder</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/main.css">
<link rel="stylesheet" href="/css/components.css">
</head>
<body>
<nav class="navbar">
  <div class="navbar-inner">
    <a href="/" class="navbar-brand">✈ Airfinder</a>
    <div class="navbar-links">
      <a href="/" class="navbar-link">Search Flights</a>
      <a href="#" class="navbar-link" data-auth-logout>Logout</a>
    </div>
  </div>
</nav>
<div class="container">
  <div class="account-layout">
    <aside class="account-sidebar">
      <div class="account-avatar" id="avatar">JD</div>
      <div class="account-name" id="user-name">Loading...</div>
      <div class="account-email" id="user-email"></div>
      <ul class="account-nav">
        <li><a href="/account/dashboard.html" class="active">🏠 Dashboard</a></li>
        <li><a href="/account/bookings.html">🎫 My Bookings</a></li>
        <li><a href="/" >✈ Search Flights</a></li>
        <li><a href="#" data-auth-logout>🚪 Logout</a></li>
      </ul>
    </aside>
    <main>
      <h2 class="mb-3">Welcome back, <span id="greeting-name">—</span>!</h2>
      <div class="stat-grid">
        <div class="stat-card green">
          <div class="stat-label">Total Bookings</div>
          <div class="stat-value" id="stat-bookings">—</div>
          <div class="stat-icon">🎫</div>
        </div>
        <div class="stat-card blue">
          <div class="stat-label">Total Spent</div>
          <div class="stat-value" id="stat-spent">—</div>
          <div class="stat-icon">💰</div>
        </div>
        <div class="stat-card amber">
          <div class="stat-label">Upcoming Trips</div>
          <div class="stat-value" id="stat-upcoming">—</div>
          <div class="stat-icon">✈</div>
        </div>
      </div>
      <h3 class="mb-2 mt-4">Recent Bookings</h3>
      <div id="recent-bookings"><div class="spinner"></div></div>
      <div class="mt-3 text-center">
        <a href="/" class="btn btn-primary">+ Book a New Flight</a>
      </div>
    </main>
  </div>
</div>
<script src="/js/api.js"></script>
<script src="/js/auth.js"></script>
<script>
document.addEventListener('DOMContentLoaded', async () => {
  if (!Auth.requireLogin()) return;
  const user = Auth.getUser();
  if (!user) return;
  document.getElementById('avatar').textContent = (user.first_name?.[0]||'') + (user.last_name?.[0]||'');
  document.getElementById('user-name').textContent = `${user.first_name} ${user.last_name}`;
  document.getElementById('user-email').textContent = user.email;
  document.getElementById('greeting-name').textContent = user.first_name;

  try {
    const bookings = await api.get('/bookings');
    document.getElementById('stat-bookings').textContent = bookings.length;
    const spent = bookings.filter(b => b.status === 'confirmed').reduce((s, b) => s + b.pricing.total, 0);
    document.getElementById('stat-spent').textContent = `$${spent.toFixed(2)}`;
    const now = new Date().toISOString().split('T')[0];
    const upcoming = bookings.filter(b => b.status === 'confirmed' && b.departure_date >= now).length;
    document.getElementById('stat-upcoming').textContent = upcoming;

    const recent = bookings.slice(0, 5);
    if (recent.length === 0) {
      document.getElementById('recent-bookings').innerHTML = '<p class="text-gray">No bookings yet. <a href="/">Search for a flight</a></p>';
    } else {
      document.getElementById('recent-bookings').innerHTML = recent.map(b => `
        <div class="booking-card">
          <div class="booking-card-header">
            <span class="booking-ref">${b.reference}</span>
            <span class="badge ${b.status === 'confirmed' ? 'badge-green' : b.status === 'cancelled' ? 'badge-red' : 'badge-amber'}">${b.status}</span>
          </div>
          <div class="booking-card-body">
            <div class="booking-route">${b.origin} → ${b.destination}</div>
            <div class="booking-detail">${b.airline} · ${b.departure_date} · $${b.pricing.total.toFixed(2)}</div>
          </div>
        </div>`).join('');
    }
  } catch (e) {
    document.getElementById('recent-bookings').innerHTML = '<p class="text-gray">Could not load bookings.</p>';
  }
});
</script>
</body>
</html>

```

## FILE: frontend/account/bookings.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>My Bookings — Airfinder</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/main.css">
<link rel="stylesheet" href="/css/components.css">
</head>
<body>
<nav class="navbar">
  <div class="navbar-inner">
    <a href="/" class="navbar-brand">✈ Airfinder</a>
    <div class="navbar-links">
      <a href="/" class="navbar-link">Search Flights</a>
      <a href="#" class="navbar-link" data-auth-logout>Logout</a>
    </div>
  </div>
</nav>
<div class="container">
  <div class="account-layout">
    <aside class="account-sidebar">
      <div class="account-avatar" id="avatar">JD</div>
      <div class="account-name" id="user-name">Loading...</div>
      <div class="account-email" id="user-email"></div>
      <ul class="account-nav">
        <li><a href="/account/dashboard.html">🏠 Dashboard</a></li>
        <li><a href="/account/bookings.html" class="active">🎫 My Bookings</a></li>
        <li><a href="/">✈ Search Flights</a></li>
        <li><a href="#" data-auth-logout>🚪 Logout</a></li>
      </ul>
    </aside>
    <main>
      <div class="flex-between mb-3">
        <h2>My Bookings</h2>
        <a href="/" class="btn btn-primary btn-sm">+ New Booking</a>
      </div>
      <div id="alert"></div>
      <div id="bookings-list"><div class="spinner"></div></div>
    </main>
  </div>
</div>
<script src="/js/api.js"></script>
<script src="/js/auth.js"></script>
<script>
document.addEventListener('DOMContentLoaded', async () => {
  if (!Auth.requireLogin()) return;
  const user = Auth.getUser();
  document.getElementById('avatar').textContent = (user.first_name?.[0]||'') + (user.last_name?.[0]||'');
  document.getElementById('user-name').textContent = `${user.first_name} ${user.last_name}`;
  document.getElementById('user-email').textContent = user.email;

  try {
    const bookings = await api.get('/bookings');
    if (bookings.length === 0) {
      document.getElementById('bookings-list').innerHTML = '<div class="card card-body text-center"><p class="text-gray">No bookings yet.</p><a href="/" class="btn btn-primary mt-2">Search Flights</a></div>';
      return;
    }
    document.getElementById('bookings-list').innerHTML = bookings.map(b => `
      <div class="booking-card">
        <div class="booking-card-header">
          <span class="booking-ref">${b.reference}</span>
          <div style="display:flex;gap:8px;align-items:center;">
            <span class="badge ${b.status === 'confirmed' ? 'badge-green' : b.status === 'cancelled' ? 'badge-red' : 'badge-amber'}">${b.status}</span>
            ${b.status === 'confirmed' ? `<button class="btn btn-danger btn-sm" onclick="cancelBooking('${b.id}')">Cancel</button>` : ''}
          </div>
        </div>
        <div class="booking-card-body">
          <div class="booking-route">${b.origin} → ${b.destination}</div>
          <div class="booking-detail">${b.airline}${b.flight_number ? ' · ' + b.flight_number : ''} · ${b.departure_date}</div>
          <div class="booking-detail">Cabin: ${b.cabin_class} · Passengers: ${b.passenger_count}</div>
          <div style="margin-top:10px;display:flex;flex-wrap:wrap;gap:8px;">
            <span class="cost-item">Base $${b.pricing.base_fare?.toFixed(2)}</span>
            <span class="cost-item">Fee $${b.pricing.service_fee?.toFixed(2)}</span>
            <span class="cost-item highlight">Total $${b.pricing.total?.toFixed(2)}</span>
          </div>
        </div>
      </div>`).join('');
  } catch {
    document.getElementById('bookings-list').innerHTML = '<p class="text-gray">Could not load bookings.</p>';
  }
});

async function cancelBooking(id) {
  if (!confirm('Cancel this booking?')) return;
  try {
    await api.post(`/bookings/${id}/cancel`, {});
    document.getElementById('alert').innerHTML = '<div class="alert alert-success">Booking cancelled.</div>';
    location.reload();
  } catch (e) {
    document.getElementById('alert').innerHTML = `<div class="alert alert-error">${e.message}</div>`;
  }
}
</script>
</body>
</html>

```

## FILE: frontend/admin/login.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Staff Login — Airfinder</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/main.css">
<link rel="stylesheet" href="/css/components.css">
<link rel="stylesheet" href="/css/admin.css">
</head>
<body>
<div class="auth-page" style="background:linear-gradient(135deg,#1f2937 0%,#374151 100%);">
  <div class="auth-card">
    <div class="auth-logo">
      <div class="auth-logo-text" style="color:var(--green);">✈ Airfinder</div>
      <div class="auth-logo-sub">Staff Portal — Authorized Access Only</div>
    </div>
    <h2 class="auth-title">Staff Sign In</h2>
    <p class="auth-sub">Use your company credentials provided by your administrator.</p>
    <div id="alert"></div>
    <form id="staff-login-form">
      <div class="form-group">
        <label class="form-label">Email</label>
        <input class="form-control" id="email" type="email" placeholder="your@airfinder.com" required autocomplete="email">
      </div>
      <div class="form-group">
        <label class="form-label">Password</label>
        <div class="password-toggle">
          <input class="form-control" id="password" type="password" placeholder="Your password" required autocomplete="current-password">
          <button type="button" class="toggle-btn" id="toggle-pw">👁</button>
        </div>
      </div>
      <button class="btn btn-primary btn-full mt-2" type="submit" id="submit-btn">Sign In to Staff Portal</button>
    </form>
    <div class="auth-footer mt-3">
      <a href="/" class="text-sm text-gray">← Customer site</a>
    </div>
  </div>
</div>
<script src="/js/api.js"></script>
<script src="/js/auth.js"></script>
<script>
document.addEventListener('DOMContentLoaded', () => {
  // Redirect if already staff-logged in
  if (Auth.isLoggedIn() && Auth.isStaff()) {
    window.location.href = '/admin/dashboard.html';
    return;
  }

  document.getElementById('toggle-pw').addEventListener('click', () => {
    const pw = document.getElementById('password');
    pw.type = pw.type === 'password' ? 'text' : 'password';
  });

  document.getElementById('staff-login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('submit-btn');
    btn.disabled = true; btn.textContent = 'Signing in...';
    clearAlert();
    try {
      const data = await api.post('/staff/auth/login', {
        email: document.getElementById('email').value,
        password: document.getElementById('password').value,
      });
      Auth.saveStaff(data.token, data.staff);

      if (data.must_change_password) {
        window.location.href = '/admin/change-password.html';
      } else {
        window.location.href = '/admin/dashboard.html';
      }
    } catch (e) {
      showAlert(e.message || 'Login failed. Check your credentials.');
      btn.disabled = false; btn.textContent = 'Sign In to Staff Portal';
    }
  });
});
function showAlert(msg) { document.getElementById('alert').innerHTML = `<div class="alert alert-error">${msg}</div>`; }
function clearAlert() { document.getElementById('alert').innerHTML = ''; }
</script>
</body>
</html>

```

## FILE: frontend/admin/change-password.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Change Password — Airfinder Staff</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/main.css">
<link rel="stylesheet" href="/css/components.css">
<link rel="stylesheet" href="/css/admin.css">
</head>
<body>
<div class="force-change-wrapper">
  <div class="force-change-card">
    <div class="force-change-icon">🔐</div>
    <h2 style="text-align:center;margin-bottom:8px;">Change Your Password</h2>
    <p class="text-gray text-sm text-center mb-3">You are using a temporary password. You must set a new password before continuing.</p>

    <div class="alert alert-warning">⚠ This is required on first login and cannot be skipped.</div>
    <div id="alert"></div>

    <form id="change-pw-form">
      <div class="form-group">
        <label class="form-label">Current (Temporary) Password</label>
        <div class="password-toggle">
          <input class="form-control" id="current_password" type="password" required placeholder="Your temporary password">
          <button type="button" class="toggle-btn" onclick="togglePw('current_password')">👁</button>
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">New Password</label>
        <div class="password-toggle">
          <input class="form-control" id="new_password" type="password" required placeholder="Min 8 characters">
          <button type="button" class="toggle-btn" onclick="togglePw('new_password')">👁</button>
        </div>
        <div class="strength-bar mt-1"><div class="strength-fill" id="strength-fill" style="width:0;background:var(--red);"></div></div>
      </div>
      <div class="form-group">
        <label class="form-label">Confirm New Password</label>
        <input class="form-control" id="confirm_password" type="password" required placeholder="Repeat new password">
      </div>
      <button class="btn btn-primary btn-full mt-2" type="submit" id="submit-btn">Set New Password</button>
    </form>
  </div>
</div>
<script src="/js/api.js"></script>
<script src="/js/auth.js"></script>
<script>
document.getElementById('new_password').addEventListener('input', function() {
  const v = this.value;
  let score = [v.length >= 8, /[A-Z]/.test(v), /[0-9]/.test(v), /[^A-Za-z0-9]/.test(v)].filter(Boolean).length;
  const colors = ['var(--red)', 'var(--red)', 'var(--amber)', 'var(--green-light)', 'var(--green)'];
  document.getElementById('strength-fill').style.width = `${score * 25}%`;
  document.getElementById('strength-fill').style.background = colors[score];
});

document.getElementById('change-pw-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const np = document.getElementById('new_password').value;
  const cp = document.getElementById('confirm_password').value;
  if (np !== cp) { showAlert('Passwords do not match.', 'error'); return; }
  if (np.length < 8) { showAlert('Password must be at least 8 characters.', 'error'); return; }

  const btn = document.getElementById('submit-btn');
  btn.disabled = true; btn.textContent = 'Saving...';
  try {
    const data = await api.post('/staff/auth/change-password', {
      current_password: document.getElementById('current_password').value,
      new_password: np,
    });
    Auth.saveStaff(data.token, data.staff);
    showAlert('Password changed successfully! Redirecting...', 'success');
    setTimeout(() => { window.location.href = '/admin/dashboard.html'; }, 1500);
  } catch (e) {
    showAlert(e.message || 'Failed to change password.', 'error');
    btn.disabled = false; btn.textContent = 'Set New Password';
  }
});

function togglePw(id) {
  const el = document.getElementById(id);
  el.type = el.type === 'password' ? 'text' : 'password';
}
function showAlert(msg, type = 'error') {
  document.getElementById('alert').innerHTML = `<div class="alert alert-${type}">${msg}</div>`;
}
</script>
</body>
</html>

```

## FILE: frontend/admin/dashboard.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard — Airfinder Admin</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/main.css">
<link rel="stylesheet" href="/css/admin.css">
</head>
<body class="admin-body">

<!-- Sidebar -->
<aside class="admin-sidebar" id="sidebar">
  <div class="admin-sidebar-logo">
    <div class="admin-logo-text">✈ Airfinder</div>
    <div class="admin-logo-sub">Staff Portal</div>
  </div>
  <nav class="admin-nav">
    <div class="admin-nav-section">Main</div>
    <a href="/admin/dashboard.html" class="admin-nav-link active"><span class="admin-nav-icon">📊</span> Dashboard</a>
    <a href="/admin/bookings.html" class="admin-nav-link"><span class="admin-nav-icon">🎫</span> Bookings</a>
    <a href="/admin/customers.html" class="admin-nav-link"><span class="admin-nav-icon">👥</span> Customers</a>
    <div class="admin-nav-section" data-role-only="super_admin,admin">Management</div>
    <a href="/admin/staff.html" class="admin-nav-link" data-role-only="super_admin,admin"><span class="admin-nav-icon">🏢</span> Staff</a>
    <a href="/admin/finance.html" class="admin-nav-link" data-role-only="super_admin,admin,finance"><span class="admin-nav-icon">💰</span> Finance</a>
    <a href="/admin/settings.html" class="admin-nav-link" data-role-only="super_admin"><span class="admin-nav-icon">⚙️</span> Settings</a>
  </nav>
  <div class="admin-sidebar-footer">
    <div class="admin-user-info">
      <div class="admin-avatar-sm" id="sidebar-avatar">SA</div>
      <div>
        <div class="admin-user-name" id="sidebar-name">Loading...</div>
        <div class="admin-user-role" id="sidebar-role">—</div>
      </div>
    </div>
    <button class="admin-logout-btn" data-admin-logout>🚪 Sign Out</button>
  </div>
</aside>

<div class="admin-main">
  <div class="admin-topbar">
    <div class="admin-page-title">Dashboard</div>
    <div class="admin-topbar-actions">
      <a href="/" target="_blank" class="btn btn-secondary btn-sm">🌐 View Site</a>
    </div>
  </div>
  <div class="admin-content">
    <div id="alert-container"></div>

    <div class="stat-grid" id="stat-grid">
      <div class="stat-card"><div class="spinner"></div></div>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:4px;" id="tables-row">
      <div class="table-card">
        <div class="table-card-header">
          <div class="table-card-title">Recent Bookings</div>
          <a href="/admin/bookings.html" class="btn btn-secondary btn-sm">View All</a>
        </div>
        <div class="table-wrapper">
          <table>
            <thead><tr><th>Ref</th><th>Route</th><th>Total</th><th>Status</th></tr></thead>
            <tbody id="recent-bookings-tbody"><tr><td colspan="4"><div class="spinner" style="margin:12px auto;"></div></td></tr></tbody>
          </table>
        </div>
      </div>
      <div class="table-card">
        <div class="table-card-header">
          <div class="table-card-title">Recent Customers</div>
          <a href="/admin/customers.html" class="btn btn-secondary btn-sm">View All</a>
        </div>
        <div class="table-wrapper">
          <table>
            <thead><tr><th>Name</th><th>Email</th><th>Bookings</th></tr></thead>
            <tbody id="recent-customers-tbody"><tr><td colspan="3"><div class="spinner" style="margin:12px auto;"></div></td></tr></tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</div>

<script src="/js/api.js"></script>
<script src="/js/auth.js"></script>
<script src="/js/admin.js"></script>
<script>
document.addEventListener('DOMContentLoaded', async () => {
  if (!Auth.requireStaff()) return;

  const [dashData, bookingsData, customersData] = await Promise.all([
    Admin.loadDashboard().catch(() => null),
    Admin.loadAllBookings(1).catch(() => null),
    Admin.loadCustomers(1).catch(() => null),
  ]);

  if (dashData) {
    const b = dashData.bookings;
    const r = dashData.revenue;
    let html = `
      <div class="stat-card green"><div class="stat-label">Total Bookings</div><div class="stat-value">${b.total}</div><div class="stat-icon">🎫</div></div>
      <div class="stat-card blue"><div class="stat-label">Confirmed</div><div class="stat-value">${b.confirmed}</div><div class="stat-icon">✅</div></div>
      <div class="stat-card amber"><div class="stat-label">Total Revenue</div><div class="stat-value">${Admin.formatCurrency(r.total_usd)}</div><div class="stat-icon">💰</div></div>
      <div class="stat-card green"><div class="stat-label">Total Customers</div><div class="stat-value">${dashData.customers}</div><div class="stat-icon">👥</div></div>`;
    if (dashData.staff !== undefined) {
      html += `<div class="stat-card"><div class="stat-label">Staff Members</div><div class="stat-value">${dashData.staff}</div><div class="stat-icon">🏢</div></div>`;
    }
    document.getElementById('stat-grid').innerHTML = html;
  }

  if (bookingsData?.bookings) {
    document.getElementById('recent-bookings-tbody').innerHTML =
      bookingsData.bookings.slice(0,8).map(b => `
        <tr>
          <td class="td-mono">${b.reference}</td>
          <td>${b.origin}→${b.destination}</td>
          <td>${Admin.formatCurrency(b.pricing.total)}</td>
          <td>${Admin.statusBadge(b.status)}</td>
        </tr>`).join('') || '<tr><td colspan="4" class="text-gray">No bookings</td></tr>';
  }

  if (customersData?.customers) {
    document.getElementById('recent-customers-tbody').innerHTML =
      customersData.customers.slice(0,8).map(c => `
        <tr>
          <td>${c.first_name} ${c.last_name}</td>
          <td class="text-sm">${c.email}</td>
          <td>${c.booking_count}</td>
        </tr>`).join('') || '<tr><td colspan="3" class="text-gray">No customers</td></tr>';
  }
});
</script>
</body>
</html>

```

## FILE: frontend/admin/staff.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Staff Management — Airfinder</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/main.css">
<link rel="stylesheet" href="/css/admin.css">
</head>
<body class="admin-body">
<aside class="admin-sidebar">
  <div class="admin-sidebar-logo"><div class="admin-logo-text">✈ Airfinder</div><div class="admin-logo-sub">Staff Portal</div></div>
  <nav class="admin-nav">
    <div class="admin-nav-section">Main</div>
    <a href="/admin/dashboard.html" class="admin-nav-link"><span class="admin-nav-icon">📊</span> Dashboard</a>
    <a href="/admin/bookings.html" class="admin-nav-link"><span class="admin-nav-icon">🎫</span> Bookings</a>
    <a href="/admin/customers.html" class="admin-nav-link"><span class="admin-nav-icon">👥</span> Customers</a>
    <div class="admin-nav-section">Management</div>
    <a href="/admin/staff.html" class="admin-nav-link active"><span class="admin-nav-icon">🏢</span> Staff</a>
    <a href="/admin/finance.html" class="admin-nav-link"><span class="admin-nav-icon">💰</span> Finance</a>
    <a href="/admin/settings.html" class="admin-nav-link" data-role-only="super_admin"><span class="admin-nav-icon">⚙️</span> Settings</a>
  </nav>
  <div class="admin-sidebar-footer">
    <div class="admin-user-info"><div class="admin-avatar-sm" id="sidebar-avatar">SA</div><div><div class="admin-user-name" id="sidebar-name">—</div><div class="admin-user-role" id="sidebar-role">—</div></div></div>
    <button class="admin-logout-btn" data-admin-logout>🚪 Sign Out</button>
  </div>
</aside>
<div class="admin-main">
  <div class="admin-topbar">
    <div class="admin-page-title">Staff Management</div>
    <button class="btn btn-primary btn-sm" onclick="openCreateModal()">+ Add Staff Member</button>
  </div>
  <div class="admin-content">
    <div id="alert-container"></div>
    <div class="table-card">
      <div class="table-toolbar">
        <div class="toolbar-search"><span class="toolbar-search-icon">🔍</span><input type="text" id="search-input" placeholder="Search staff..."></div>
      </div>
      <div class="table-wrapper">
        <table>
          <thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Status</th><th>Last Login</th><th>Actions</th></tr></thead>
          <tbody id="staff-tbody"><tr><td colspan="6"><div class="spinner" style="margin:16px auto;"></div></td></tr></tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<!-- Create Staff Modal -->
<div class="modal-overlay hidden" id="create-modal">
  <div class="modal">
    <button class="modal-close" onclick="closeModal()">✕</button>
    <h3 class="mb-3">Add Staff Member</h3>
    <div id="modal-alert"></div>
    <form id="create-staff-form">
      <div class="form-row">
        <div class="form-group"><label class="form-label">First Name</label><input class="form-control" id="cf_first" required placeholder="John"></div>
        <div class="form-group"><label class="form-label">Last Name</label><input class="form-control" id="cf_last" required placeholder="Doe"></div>
      </div>
      <div class="form-group"><label class="form-label">Email</label><input class="form-control" id="cf_email" type="email" required placeholder="john@airfinder.com"></div>
      <div class="form-group">
        <label class="form-label">Role</label>
        <div class="role-select">
          <label class="role-option"><input type="radio" name="cf_role" value="agent" required checked><div class="role-option-label">Agent</div><div class="role-option-desc">Bookings & customer support</div></label>
          <label class="role-option"><input type="radio" name="cf_role" value="finance"><div class="role-option-label">Finance</div><div class="role-option-desc">Revenue & reports</div></label>
          <label class="role-option"><input type="radio" name="cf_role" value="admin"><div class="role-option-label">Admin</div><div class="role-option-desc">Full operations access</div></label>
        </div>
      </div>
      <div class="alert alert-info text-sm">A temporary password will be generated and emailed to the staff member. They must change it on first login.</div>
      <div style="display:flex;gap:10px;margin-top:16px;">
        <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
        <button type="submit" class="btn btn-primary" style="flex:1;" id="create-btn">Create Account</button>
      </div>
    </form>
    <div id="create-success" class="hidden">
      <div class="alert alert-success">✓ Staff account created! Credentials sent to email.</div>
      <div class="card card-body mt-2" id="cred-box"></div>
      <button class="btn btn-primary w-full mt-2" onclick="closeModal()">Done</button>
    </div>
  </div>
</div>

<script src="/js/api.js"></script>
<script src="/js/auth.js"></script>
<script src="/js/admin.js"></script>
<script>
let staffList = [];

document.addEventListener('DOMContentLoaded', async () => {
  if (!Auth.requireRole('super_admin', 'admin')) return;
  loadStaff();
  document.getElementById('search-input').addEventListener('input', function() {
    const q = this.value.toLowerCase();
    renderStaff(staffList.filter(s => s.email.includes(q) || s.first_name.toLowerCase().includes(q) || s.last_name.toLowerCase().includes(q)));
  });
});

async function loadStaff() {
  try {
    staffList = await Admin.loadStaff();
    renderStaff(staffList);
  } catch { document.getElementById('staff-tbody').innerHTML = '<tr><td colspan="6" class="text-gray">Failed to load staff.</td></tr>'; }
}

function renderStaff(list) {
  if (!list.length) { document.getElementById('staff-tbody').innerHTML = '<tr><td colspan="6" class="text-gray" style="text-align:center;padding:20px;">No staff found.</td></tr>'; return; }
  document.getElementById('staff-tbody').innerHTML = list.map(s => `
    <tr>
      <td><strong>${s.first_name} ${s.last_name}</strong></td>
      <td>${s.email}</td>
      <td>${Admin.roleBadge(s.role)}</td>
      <td>${s.is_active ? '<span class="badge badge-green">Active</span>' : '<span class="badge badge-red">Inactive</span>'}</td>
      <td class="text-sm text-gray">${s.last_login ? new Date(s.last_login).toLocaleDateString() : 'Never'}</td>
      <td style="display:flex;gap:6px;">
        <button class="btn btn-secondary btn-sm" onclick="resetPassword('${s.id}','${s.first_name}')">Reset PW</button>
        <button class="btn btn-sm ${s.is_active ? 'btn-danger' : 'btn-primary'}" onclick="toggleActive('${s.id}',${!s.is_active})">${s.is_active ? 'Deactivate' : 'Activate'}</button>
      </td>
    </tr>`).join('');
}

function openCreateModal() { document.getElementById('create-modal').classList.remove('hidden'); document.getElementById('create-success').classList.add('hidden'); document.getElementById('create-staff-form').classList.remove('hidden'); }
function closeModal() { document.getElementById('create-modal').classList.add('hidden'); loadStaff(); }

document.getElementById('create-staff-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = document.getElementById('create-btn');
  btn.disabled = true; btn.textContent = 'Creating...';
  try {
    const data = await Admin.createStaff({
      first_name: document.getElementById('cf_first').value,
      last_name: document.getElementById('cf_last').value,
      email: document.getElementById('cf_email').value,
      role: document.querySelector('input[name=cf_role]:checked').value,
    });
    document.getElementById('create-staff-form').classList.add('hidden');
    document.getElementById('cred-box').innerHTML = `<p class="text-sm"><strong>Email:</strong> ${data.staff.email}</p><p class="text-sm mt-1"><strong>Temp Password:</strong> <code style="background:var(--gray-100);padding:2px 6px;border-radius:4px;">${data.temp_password}</code></p><p class="text-xs text-gray mt-1">Share this securely. Staff will be forced to change on first login.</p>`;
    document.getElementById('create-success').classList.remove('hidden');
  } catch (e) {
    document.getElementById('modal-alert').innerHTML = `<div class="alert alert-error">${e.message}</div>`;
  } finally { btn.disabled = false; btn.textContent = 'Create Account'; }
});

async function resetPassword(id, name) {
  if (!confirm(`Reset password for ${name}?`)) return;
  try {
    const data = await Admin.resetStaffPassword(id);
    Admin.showToast(`Password reset. Temp: ${data.temp_password}`);
  } catch (e) { Admin.showToast(e.message, 'error'); }
}

async function toggleActive(id, isActive) {
  try {
    await Admin.updateStaff(id, { is_active: isActive });
    Admin.showToast(isActive ? 'Staff activated' : 'Staff deactivated');
    loadStaff();
  } catch (e) { Admin.showToast(e.message, 'error'); }
}
</script>
</body>
</html>

```

## FILE: frontend/admin/bookings.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>All Bookings — Airfinder Admin</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/main.css">
<link rel="stylesheet" href="/css/admin.css">
</head>
<body class="admin-body">
<aside class="admin-sidebar">
  <div class="admin-sidebar-logo"><div class="admin-logo-text">✈ Airfinder</div><div class="admin-logo-sub">Staff Portal</div></div>
  <nav class="admin-nav">
    <div class="admin-nav-section">Main</div>
    <a href="/admin/dashboard.html" class="admin-nav-link"><span class="admin-nav-icon">📊</span> Dashboard</a>
    <a href="/admin/bookings.html" class="admin-nav-link active"><span class="admin-nav-icon">🎫</span> Bookings</a>
    <a href="/admin/customers.html" class="admin-nav-link"><span class="admin-nav-icon">👥</span> Customers</a>
    <div class="admin-nav-section">Management</div>
    <a href="/admin/staff.html" class="admin-nav-link" data-role-only="super_admin,admin"><span class="admin-nav-icon">🏢</span> Staff</a>
    <a href="/admin/finance.html" class="admin-nav-link"><span class="admin-nav-icon">💰</span> Finance</a>
    <a href="/admin/settings.html" class="admin-nav-link" data-role-only="super_admin"><span class="admin-nav-icon">⚙️</span> Settings</a>
  </nav>
  <div class="admin-sidebar-footer">
    <div class="admin-user-info"><div class="admin-avatar-sm" id="sidebar-avatar">SA</div><div><div class="admin-user-name" id="sidebar-name">—</div><div class="admin-user-role" id="sidebar-role">—</div></div></div>
    <button class="admin-logout-btn" data-admin-logout>🚪 Sign Out</button>
  </div>
</aside>
<div class="admin-main">
  <div class="admin-topbar"><div class="admin-page-title">All Bookings</div></div>
  <div class="admin-content">
    <div id="alert-container"></div>
    <div class="table-card">
      <div class="table-toolbar">
        <select class="toolbar-select" id="status-filter">
          <option value="">All Statuses</option>
          <option value="confirmed">Confirmed</option>
          <option value="pending">Pending</option>
          <option value="cancelled">Cancelled</option>
          <option value="refunded">Refunded</option>
        </select>
      </div>
      <div class="table-wrapper">
        <table>
          <thead><tr><th>Reference</th><th>Customer</th><th>Route</th><th>Date</th><th>Airline</th><th>Total</th><th>Status</th><th>Actions</th></tr></thead>
          <tbody id="bookings-tbody"><tr><td colspan="8"><div class="spinner" style="margin:16px auto;"></div></td></tr></tbody>
        </table>
      </div>
      <div class="pagination" id="pagination"></div>
    </div>
  </div>
</div>

<script src="/js/api.js"></script>
<script src="/js/auth.js"></script>
<script src="/js/admin.js"></script>
<script>
let currentPage = 1;

document.addEventListener('DOMContentLoaded', async () => {
  if (!Auth.requireStaff()) return;
  loadBookings();
  document.getElementById('status-filter').addEventListener('change', () => { currentPage = 1; loadBookings(); });
});

async function loadBookings() {
  const status = document.getElementById('status-filter').value;
  try {
    const data = await Admin.loadAllBookings(currentPage, status);
    renderBookings(data.bookings);
    renderPagination(data.pages, data.page);
  } catch { document.getElementById('bookings-tbody').innerHTML = '<tr><td colspan="8" class="text-gray">Failed to load.</td></tr>'; }
}

function renderBookings(bookings) {
  if (!bookings.length) { document.getElementById('bookings-tbody').innerHTML = '<tr><td colspan="8" class="text-gray" style="text-align:center;padding:20px;">No bookings found.</td></tr>'; return; }
  document.getElementById('bookings-tbody').innerHTML = bookings.map(b => `
    <tr>
      <td class="td-mono">${b.reference}</td>
      <td class="text-sm">${b.user_id?.slice(0,8)}...</td>
      <td><strong>${b.origin} → ${b.destination}</strong></td>
      <td>${b.departure_date}</td>
      <td class="text-sm">${b.airline}</td>
      <td><strong>${Admin.formatCurrency(b.pricing.total)}</strong></td>
      <td>${Admin.statusBadge(b.status)}</td>
      <td>
        <select onchange="updateStatus('${b.id}',this.value)" style="padding:4px 8px;border:1px solid var(--gray-200);border-radius:4px;font-size:12px;">
          <option value="">Change...</option>
          <option value="confirmed">Confirm</option>
          <option value="cancelled">Cancel</option>
          <option value="refunded">Refund</option>
        </select>
      </td>
    </tr>`).join('');
}

function renderPagination(pages, current) {
  if (pages <= 1) { document.getElementById('pagination').innerHTML = ''; return; }
  let html = `<button class="page-btn" onclick="changePage(${current-1})" ${current<=1?'disabled':''}>← Prev</button>`;
  for (let i = 1; i <= pages; i++) html += `<button class="page-btn ${i===current?'active':''}" onclick="changePage(${i})">${i}</button>`;
  html += `<button class="page-btn" onclick="changePage(${current+1})" ${current>=pages?'disabled':''}>Next →</button>`;
  document.getElementById('pagination').innerHTML = html;
}

function changePage(p) { currentPage = p; loadBookings(); }

async function updateStatus(id, status) {
  if (!status) return;
  try {
    await Admin.updateBooking(id, { status });
    Admin.showToast(`Booking status updated to ${status}`);
    loadBookings();
  } catch (e) { Admin.showToast(e.message, 'error'); }
}
</script>
</body>
</html>

```

## FILE: frontend/admin/customers.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Customers — Airfinder Admin</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/main.css">
<link rel="stylesheet" href="/css/admin.css">
</head>
<body class="admin-body">
<aside class="admin-sidebar">
  <div class="admin-sidebar-logo"><div class="admin-logo-text">✈ Airfinder</div><div class="admin-logo-sub">Staff Portal</div></div>
  <nav class="admin-nav">
    <div class="admin-nav-section">Main</div>
    <a href="/admin/dashboard.html" class="admin-nav-link"><span class="admin-nav-icon">📊</span> Dashboard</a>
    <a href="/admin/bookings.html" class="admin-nav-link"><span class="admin-nav-icon">🎫</span> Bookings</a>
    <a href="/admin/customers.html" class="admin-nav-link active"><span class="admin-nav-icon">👥</span> Customers</a>
    <div class="admin-nav-section">Management</div>
    <a href="/admin/staff.html" class="admin-nav-link" data-role-only="super_admin,admin"><span class="admin-nav-icon">🏢</span> Staff</a>
    <a href="/admin/finance.html" class="admin-nav-link"><span class="admin-nav-icon">💰</span> Finance</a>
    <a href="/admin/settings.html" class="admin-nav-link" data-role-only="super_admin"><span class="admin-nav-icon">⚙️</span> Settings</a>
  </nav>
  <div class="admin-sidebar-footer">
    <div class="admin-user-info"><div class="admin-avatar-sm" id="sidebar-avatar">SA</div><div><div class="admin-user-name" id="sidebar-name">—</div><div class="admin-user-role" id="sidebar-role">—</div></div></div>
    <button class="admin-logout-btn" data-admin-logout>🚪 Sign Out</button>
  </div>
</aside>
<div class="admin-main">
  <div class="admin-topbar"><div class="admin-page-title">Customer Management</div></div>
  <div class="admin-content">
    <div class="table-card">
      <div class="table-toolbar">
        <div class="toolbar-search">
          <span class="toolbar-search-icon">🔍</span>
          <input type="text" id="search-input" placeholder="Search by name or email...">
        </div>
      </div>
      <div class="table-wrapper">
        <table>
          <thead><tr><th>Name</th><th>Email</th><th>Phone</th><th>Bookings</th><th>Total Spent</th><th>Joined</th><th>Status</th></tr></thead>
          <tbody id="customers-tbody"><tr><td colspan="7"><div class="spinner" style="margin:16px auto;"></div></td></tr></tbody>
        </table>
      </div>
      <div class="pagination" id="pagination"></div>
    </div>
  </div>
</div>

<script src="/js/api.js"></script>
<script src="/js/auth.js"></script>
<script src="/js/admin.js"></script>
<script>
let currentPage = 1;
let searchTimer;

document.addEventListener('DOMContentLoaded', () => {
  if (!Auth.requireStaff()) return;
  loadCustomers();
  document.getElementById('search-input').addEventListener('input', function() {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => { currentPage = 1; loadCustomers(this.value); }, 300);
  });
});

async function loadCustomers(search = '') {
  try {
    const data = await Admin.loadCustomers(currentPage, search);
    renderCustomers(data.customers);
    renderPagination(data.pages, data.page);
  } catch { document.getElementById('customers-tbody').innerHTML = '<tr><td colspan="7" class="text-gray">Failed to load.</td></tr>'; }
}

function renderCustomers(customers) {
  if (!customers.length) { document.getElementById('customers-tbody').innerHTML = '<tr><td colspan="7" class="text-gray" style="text-align:center;padding:20px;">No customers found.</td></tr>'; return; }
  document.getElementById('customers-tbody').innerHTML = customers.map(c => `
    <tr>
      <td><strong>${escapeHtml(c.first_name)} ${escapeHtml(c.last_name)}</strong></td>
      <td>${escapeHtml(c.email)}</td>
      <td>${escapeHtml(c.phone) || '—'}</td>
      <td>${c.booking_count}</td>
      <td>${Admin.formatCurrency(c.total_spent)}</td>
      <td class="text-sm text-gray">${new Date(c.created_at).toLocaleDateString()}</td>
      <td>${c.is_active ? '<span class="badge badge-green">Active</span>' : '<span class="badge badge-red">Inactive</span>'}</td>
    </tr>`).join('');
}

function renderPagination(pages, current) {
  if (pages <= 1) { document.getElementById('pagination').innerHTML = ''; return; }
  let html = `<button class="page-btn" onclick="changePage(${current-1})" ${current<=1?'disabled':''}>← Prev</button>`;
  for (let i = 1; i <= Math.min(pages, 10); i++) html += `<button class="page-btn ${i===current?'active':''}" onclick="changePage(${i})">${i}</button>`;
  html += `<button class="page-btn" onclick="changePage(${current+1})" ${current>=pages?'disabled':''}>Next →</button>`;
  document.getElementById('pagination').innerHTML = html;
}

function changePage(p) { currentPage = p; loadCustomers(document.getElementById('search-input').value); }
</script>
</body>
</html>

```

## FILE: frontend/admin/finance.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Finance — Airfinder Admin</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/main.css">
<link rel="stylesheet" href="/css/admin.css">
</head>
<body class="admin-body">
<aside class="admin-sidebar">
  <div class="admin-sidebar-logo"><div class="admin-logo-text">✈ Airfinder</div><div class="admin-logo-sub">Staff Portal</div></div>
  <nav class="admin-nav">
    <div class="admin-nav-section">Main</div>
    <a href="/admin/dashboard.html" class="admin-nav-link"><span class="admin-nav-icon">📊</span> Dashboard</a>
    <a href="/admin/bookings.html" class="admin-nav-link"><span class="admin-nav-icon">🎫</span> Bookings</a>
    <a href="/admin/customers.html" class="admin-nav-link"><span class="admin-nav-icon">👥</span> Customers</a>
    <div class="admin-nav-section">Management</div>
    <a href="/admin/staff.html" class="admin-nav-link" data-role-only="super_admin,admin"><span class="admin-nav-icon">🏢</span> Staff</a>
    <a href="/admin/finance.html" class="admin-nav-link active"><span class="admin-nav-icon">💰</span> Finance</a>
    <a href="/admin/settings.html" class="admin-nav-link" data-role-only="super_admin"><span class="admin-nav-icon">⚙️</span> Settings</a>
  </nav>
  <div class="admin-sidebar-footer">
    <div class="admin-user-info"><div class="admin-avatar-sm" id="sidebar-avatar">SA</div><div><div class="admin-user-name" id="sidebar-name">—</div><div class="admin-user-role" id="sidebar-role">—</div></div></div>
    <button class="admin-logout-btn" data-admin-logout>🚪 Sign Out</button>
  </div>
</aside>
<div class="admin-main">
  <div class="admin-topbar"><div class="admin-page-title">Finance Dashboard</div></div>
  <div class="admin-content">
    <div class="revenue-grid" id="revenue-grid">
      <div class="stat-card"><div class="spinner"></div></div>
    </div>
    <div class="table-card mt-3">
      <div class="table-card-header"><div class="table-card-title">Revenue Breakdown</div></div>
      <div class="card-body" id="breakdown-body">
        <div class="spinner"></div>
      </div>
    </div>
    <div class="card card-body mt-3">
      <h4 class="mb-2">Revenue Transparency</h4>
      <p class="text-sm text-gray">Airfinder earns through a combination of transparent commission, markup, and service fees. All amounts shown are confirmed bookings only.</p>
      <div class="chart-placeholder mt-3">📈 Revenue chart — connect to analytics API for real-time data</div>
    </div>
  </div>
</div>
<script src="/js/api.js"></script>
<script src="/js/auth.js"></script>
<script src="/js/admin.js"></script>
<script>
document.addEventListener('DOMContentLoaded', async () => {
  if (!Auth.requireRole('super_admin', 'admin', 'finance')) return;
  try {
    const data = await Admin.loadFinance();
    document.getElementById('revenue-grid').innerHTML = `
      <div class="revenue-card"><div class="revenue-label">Total Revenue</div><div class="revenue-value">${Admin.formatCurrency(data.total_revenue_usd)}</div></div>
      <div class="revenue-card"><div class="revenue-label">Commission Earned</div><div class="revenue-value">${Admin.formatCurrency(data.commission_usd)}</div></div>
      <div class="revenue-card"><div class="revenue-label">Markup Revenue</div><div class="revenue-value">${Admin.formatCurrency(data.markup_usd)}</div></div>
      <div class="revenue-card"><div class="revenue-label">Service Fees</div><div class="revenue-value">${Admin.formatCurrency(data.service_fees_usd)}</div></div>
      <div class="revenue-card"><div class="revenue-label">Baggage Fees</div><div class="revenue-value">${Admin.formatCurrency(data.baggage_fees_usd)}</div></div>
      <div class="revenue-card"><div class="revenue-label">Confirmed Bookings</div><div class="revenue-value">${data.total_bookings}</div></div>`;
    document.getElementById('breakdown-body').innerHTML = `
      <div class="price-line"><span>Average booking value</span><span><strong>${Admin.formatCurrency(data.avg_booking_value)}</strong></span></div>
      <div class="price-line"><span>Commission (3% of base fare)</span><span>${Admin.formatCurrency(data.commission_usd)}</span></div>
      <div class="price-line"><span>Markup (8% of base fare)</span><span>${Admin.formatCurrency(data.markup_usd)}</span></div>
      <div class="price-line"><span>Service fee ($15/booking)</span><span>${Admin.formatCurrency(data.service_fees_usd)}</span></div>
      <div class="price-line"><span>Baggage fees</span><span>${Admin.formatCurrency(data.baggage_fees_usd)}</span></div>
      <hr class="divider">
      <div class="price-line total"><span>Total Airfinder Earnings</span><span style="color:var(--green);">${Admin.formatCurrency(data.total_revenue_usd)}</span></div>`;
  } catch (e) {
    document.getElementById('revenue-grid').innerHTML = '<p class="text-gray">No data yet. Make some bookings first!</p>';
    document.getElementById('breakdown-body').innerHTML = '';
  }
});
</script>
</body>
</html>

```

## FILE: frontend/admin/settings.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Settings — Airfinder Admin</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/main.css">
<link rel="stylesheet" href="/css/admin.css">
</head>
<body class="admin-body">
<aside class="admin-sidebar">
  <div class="admin-sidebar-logo"><div class="admin-logo-text">✈ Airfinder</div><div class="admin-logo-sub">Staff Portal</div></div>
  <nav class="admin-nav">
    <div class="admin-nav-section">Main</div>
    <a href="/admin/dashboard.html" class="admin-nav-link"><span class="admin-nav-icon">📊</span> Dashboard</a>
    <a href="/admin/bookings.html" class="admin-nav-link"><span class="admin-nav-icon">🎫</span> Bookings</a>
    <a href="/admin/customers.html" class="admin-nav-link"><span class="admin-nav-icon">👥</span> Customers</a>
    <div class="admin-nav-section">Management</div>
    <a href="/admin/staff.html" class="admin-nav-link"><span class="admin-nav-icon">🏢</span> Staff</a>
    <a href="/admin/finance.html" class="admin-nav-link"><span class="admin-nav-icon">💰</span> Finance</a>
    <a href="/admin/settings.html" class="admin-nav-link active"><span class="admin-nav-icon">⚙️</span> Settings</a>
  </nav>
  <div class="admin-sidebar-footer">
    <div class="admin-user-info"><div class="admin-avatar-sm" id="sidebar-avatar">SA</div><div><div class="admin-user-name" id="sidebar-name">—</div><div class="admin-user-role" id="sidebar-role">—</div></div></div>
    <button class="admin-logout-btn" data-admin-logout>🚪 Sign Out</button>
  </div>
</aside>
<div class="admin-main">
  <div class="admin-topbar"><div class="admin-page-title">System Settings</div></div>
  <div class="admin-content">
    <div class="alert alert-warning">⚠ Settings changes take effect after server restart. Contact your developer to update .env file.</div>

    <div class="card card-body mt-3" id="settings-card">
      <h3 class="mb-3">Current Configuration</h3>
      <div id="settings-body"><div class="spinner"></div></div>
    </div>

    <div class="card card-body mt-3">
      <h3 class="mb-2">Revenue Model Controls</h3>
      <p class="text-sm text-gray mb-3">These values are loaded from the .env file. To change them, update the file and restart the server.</p>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;">
        <div class="card card-body" style="background:var(--gray-50);">
          <div class="text-xs text-gray">DEFAULT_MARKUP_PERCENT</div>
          <div id="cfg-markup" class="revenue-value">—%</div>
          <div class="text-xs text-gray mt-1">Added to base fare transparently</div>
        </div>
        <div class="card card-body" style="background:var(--gray-50);">
          <div class="text-xs text-gray">DEFAULT_SERVICE_FEE_USD</div>
          <div id="cfg-fee" class="revenue-value">$—</div>
          <div class="text-xs text-gray mt-1">Flat fee per booking</div>
        </div>
        <div class="card card-body" style="background:var(--gray-50);">
          <div class="text-xs text-gray">DEFAULT_COMMISSION_PERCENT</div>
          <div id="cfg-commission" class="revenue-value">—%</div>
          <div class="text-xs text-gray mt-1">Earned from partners per booking</div>
        </div>
      </div>
    </div>

    <div class="card card-body mt-3">
      <h3 class="mb-2">B2B White-Label</h3>
      <p class="text-sm text-gray">License the Airfinder platform to travel agencies as a white-label product.</p>
      <div class="alert alert-info mt-2">B2B licensing requires custom domain + API key configuration. Contact your developer to enable.</div>
    </div>
  </div>
</div>
<script src="/js/api.js"></script>
<script src="/js/auth.js"></script>
<script src="/js/admin.js"></script>
<script>
document.addEventListener('DOMContentLoaded', async () => {
  if (!Auth.requireRole('super_admin')) return;
  try {
    const s = await api.get('/admin/settings');
    document.getElementById('cfg-markup').textContent = `${s.markup_percent}%`;
    document.getElementById('cfg-fee').textContent = `$${s.service_fee_usd}`;
    document.getElementById('cfg-commission').textContent = `${s.commission_percent}%`;
    document.getElementById('settings-body').innerHTML = `
      <div class="price-line"><span>Markup</span><span>${s.markup_percent}% of base fare</span></div>
      <div class="price-line"><span>Service Fee</span><span>$${s.service_fee_usd} per booking</span></div>
      <div class="price-line"><span>Commission</span><span>${s.commission_percent}% of base fare</span></div>`;
  } catch { document.getElementById('settings-body').innerHTML = '<p class="text-gray">Could not load settings.</p>'; }
});
</script>
</body>
</html>

```

---

## CREDENTIALS

| Account | Email | Password |
|---------|-------|----------|
| Super Admin | admin@airfinder.com | Admin@2024! |
| Staff (created by admin) | set by admin | temp password emailed, must change on first login |
| Customer | self-register at / | chosen at signup |

Admin panel: http://localhost:5000/admin/login.html

---

## VERIFICATION CHECKLIST

1. `python backend/app.py` — Flask starts on port 5000
2. http://localhost:5000 — landing page loads with green hero + AI search bar
3. Register customer at /auth/register.html — login works
4. Search flights (e.g. LOS → LHR) — 3-6 results with True Cost breakdown
5. Book a flight — 3-step flow, confirmation page shows booking ref AF-XXXXXXXX
6. Multi-city: select Multi-city tab, add 2+ legs, search, select per leg, book
7. Admin login at /admin/login.html with admin@airfinder.com / Admin@2024!
8. Admin: create staff member — temp password shown in modal
9. Staff first login → force-change-password page → after change, dashboard accessible
10. Finance role cannot access Staff Management page (access denied alert)
11. `cd backend && python -m pytest tests/ -v` — all tests pass

---

## KNOWN DEPENDENCIES

```
Flask==3.0.3
Flask-CORS==4.0.1
Flask-Limiter==3.8.0
Flask-Mail==0.10.0
PyJWT==2.9.0
bcrypt==4.2.0
SQLAlchemy==2.0.36
python-dotenv==1.0.1
pytest==8.3.4
```

Install: `pip install -r requirements.txt`

---

## REVENUE CONFIG (.env)

```
DEFAULT_MARKUP_PERCENT=8
DEFAULT_SERVICE_FEE_USD=15
DEFAULT_COMMISSION_PERCENT=3
```

True Cost = base_fare × (1 + markup/100) + service_fee + baggage_fee + seat_fee

---

*SKILL.md generated for Airfinder v1.0 — complete system reproduction guide*

---

## POST-v1 IMPROVEMENTS (applied after initial build)

### 1. Airport Database Expansion (mock_flights.py)
- Airports: 21 → 191, all with `lat`/`lon` coordinates
- New regions: Germany (13), UK (7), France (6), Benelux (4), Switzerland (2),
  Austria (2), Spain (7), Portugal (3), Italy (6), Scandinavia (5), Eastern Europe (11),
  Greece (4), Americas (27), Asia (28), Oceania (7)
- Germany airports: FRA, MUC, DUS, BER, HAM, STR, CGN, NUE, HAJ, LEJ, DRS, BSL, FKB
- Nigeria airports: LOS, ABV, PHC, KAN, ENU

### 2. Haversine Flight Duration (mock_flights.py)
- Replaced hardcoded route lookup table with great-circle distance formula
- `_haversine_km(lat1, lon1, lat2, lon2)` → km → hours at 870 km/h cruise
- `@lru_cache(maxsize=512)` on `_estimate_duration` for performance
- `arr_hour = int(...)` cast prevents float format error in f-string `{:02d}`

### 3. Airline Pool Expansion + Region Filtering (mock_flights.py)
- Airlines: 14 → 50 across 6 regions (africa, middle_east, europe, asia, americas, oceania)
- Added `longhaul: bool` field to each airline
- `_eligible_airlines(origin_region, dest_region)`:
  - Same region → only airlines from that region
  - Cross-region → longhaul from both endpoint regions + all Middle East carriers
  - Fallback: add any longhaul airline if pool < 4
- BASE_PRICES: ~30 → 471 route pairs

### 4. Airport Carrier Whitelist (mock_flights.py)
- `AIRPORT_CARRIERS` dict: maps airport codes to sets of airlines that actually serve them
- `_apply_airport_restrictions(pool, origin, destination)` called after `_eligible_airlines()`
- Prevents impossible airline-airport combos (e.g. Etihad/Turkish on DUS→PHC)
- Restricted airports:
  - PHC: Air Peace, Arik Air, IbomAir, Ethiopian Airlines, Kenya Airways, RwandAir
  - KAN: Air Peace, Arik Air, IbomAir, Ethiopian Airlines, RwandAir
  - ENU: Air Peace, Arik Air, IbomAir
  - DLA/LFW/COO/OUA/BKO/CKY: Air France, Royal Air Maroc, ASKY, Ethiopian, Air Côte d'Ivoire
  - JRO: Ethiopian, Kenya Airways, RwandAir, KLM
  - EBB: Ethiopian, Kenya Airways, RwandAir, Emirates, Qatar, Turkish
  - STR/CGN/NUE/HAJ/LEJ/DRS/FKB: Lufthansa, Eurowings, Ryanair, EasyJet, Wizz Air
  - EDI/BHX/GLA/MAN: British Airways + LCCs + limited longhaul

### 5. Flight Status / Tracking Page (frontend/flight-status.html + backend/routes/flights.py)
- New page: `/flight-status.html`
- New endpoint: `GET /api/flights/status?flight=XX&date=YYYY-MM-DD`
- Deterministic mock: `hashlib.md5(flight+date)` seeds `random.Random` — same input = same result
- Returns: airline, origin/destination with full names, scheduled/actual times, status,
  delay_minutes, gate, terminal, aircraft, baggage_belt, distance_km
- Status options: on_time (50%), delayed (15%), boarding (15%), departed (20%),
  arrived (20%), cancelled (5%) — weighted via deterministic seed
- Frontend: green gradient hero, 4-step progress bar, info grid, Web Share API button,
  8 quick-example flight lookups, URL param auto-trigger (?flight=XX&date=YYYY-MM-DD)

### 6. Flight Status Navbar Link — All Pages
Added `<a href="/flight-status.html" class="navbar-link">Flight Status</a>` to:
- frontend/index.html
- frontend/results.html
- frontend/booking.html
- frontend/multicity.html
- frontend/confirmation.html (full navbar added — was bare brand-only)
- frontend/account/dashboard.html
- frontend/account/bookings.html
- frontend/account/profile.html

### 7. Currency Localization (frontend/js/locale.js)
- All prices display in EUR (not USD)
- `fmtCurrency()` converts USD→EUR client-side using fixed rate
- EUR symbol used sitewide; dollar signs removed from all SVG icons

### 8. Forgot Password Flow (staff portal)
- `POST /api/staff/auth/forgot-password` → email reset link
- `POST /api/staff/auth/reset-password` → token-based password reset
- Frontend: /admin/forgot-password.html, /admin/reset-password.html

### 9. My Profile Page (all staff roles)
- Self-service password change available to all staff (not just super_admin)
- `/staff/profile.html` page with current password verification before change

### VERIFICATION ADDITIONS
12. http://localhost:5000/flight-status.html — enter LH401 + any future date → status card renders
13. Search DUS→PHC — only Air Peace, Ethiopian, Kenya Airways, RwandAir appear (not Emirates/Turkish)
14. Search DUS→LOS — broader pool including KLM, Air France, Emirates
15. Search FRA→JFK — only longhaul European/Middle East/US carriers appear
