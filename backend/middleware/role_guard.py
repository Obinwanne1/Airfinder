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
