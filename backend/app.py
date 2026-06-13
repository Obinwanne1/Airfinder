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

    @app.route('/api/demo-request', methods=['POST'])
    def demo_request():
        from flask import request
        import json, datetime
        data = request.get_json(silent=True) or {}
        entry = {
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'name': data.get('name', ''),
            'company': data.get('company', ''),
            'email': data.get('email', ''),
            'phone': data.get('phone', ''),
            'message': data.get('message', ''),
        }
        log_path = os.path.join(os.path.dirname(__file__), '..', 'demo_requests.log')
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')
        print(f"[DEMO REQUEST] {entry['name']} <{entry['email']}> — {entry['company']}")
        return jsonify({'message': 'Request received'}), 201

    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')

    @app.route('/auth/<path:filename>')
    def auth_pages(filename):
        return send_from_directory(os.path.join(app.static_folder, 'auth'), filename)

    @app.route('/account/<path:filename>')
    def account_pages(filename):
        return send_from_directory(os.path.join(app.static_folder, 'account'), filename)

    @app.route('/admin/<path:filename>')
    def admin_pages(filename):
        return send_from_directory(os.path.join(app.static_folder, 'admin'), filename)

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'error': 'Internal server error'}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=Config.PORT, debug=True)
