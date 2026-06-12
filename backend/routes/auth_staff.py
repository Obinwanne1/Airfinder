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
    return jsonify({
        'token': token,
        'staff': staff.to_dict(),
        'must_change_password': staff.must_change_password,
    })

@bp.route('/change-password', methods=['POST'])
def change_password():
    """Force-change temporary password — works even when must_change_password=True"""
    token = _extract_token()
    if not token:
        return jsonify({'error': 'Authorization token required'}), 401

    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=['HS256'])
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401

    staff = Staff.query.get(payload['user_id'])
    if not staff:
        return jsonify({'error': 'Staff not found'}), 404

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
    return jsonify({
        'message': 'Password changed successfully',
        'token': new_token,
        'staff': staff.to_dict(),
    })

@bp.route('/me', methods=['GET'])
@staff_required
def me():
    staff = Staff.query.get(g.user_id)
    if not staff:
        return jsonify({'error': 'Staff not found'}), 404
    return jsonify(staff.to_dict())

def _generate_staff_token(staff: Staff) -> str:
    payload = {
        'user_id': staff.id,
        'role': staff.role.value,
        'must_change_password': staff.must_change_password,
        'exp': datetime.utcnow() + timedelta(hours=12),
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET'], algorithm='HS256')

def _extract_token():
    auth = request.headers.get('Authorization', '')
    return auth[7:] if auth.startswith('Bearer ') else None
