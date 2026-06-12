import jwt
from functools import wraps
from flask import request, jsonify, current_app, g
from backend.models.user import User
from backend.models.staff import Staff

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _extract_token()
        if not token:
            return jsonify({'error': 'Authorization token required'}), 401
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=['HS256'])
            g.user_id = payload['user_id']
            g.role = payload['role']
            g.must_change_password = payload.get('must_change_password', False)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

def staff_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _extract_token()
        if not token:
            return jsonify({'error': 'Authorization token required'}), 401
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=['HS256'])
            role = payload.get('role', '')
            if role not in ('super_admin', 'admin', 'agent', 'finance'):
                return jsonify({'error': 'Staff access required'}), 403
            g.user_id = payload['user_id']
            g.role = role
            g.must_change_password = payload.get('must_change_password', False)
            # Block any action if password change is required
            if g.must_change_password:
                return jsonify({'error': 'Password change required', 'must_change_password': True}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

def _extract_token():
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    return None
