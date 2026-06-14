"""
Run this to reset the super admin password without needing to log in.
Usage: python reset_admin.py
"""
import os, sys
os.environ.setdefault('FLASK_ENV', 'development')

# Load .env
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend.app import create_app
from backend.models.database import db
from backend.models.staff import Staff, StaffRole
import bcrypt

app = create_app()
# Ensure we use the same instance path the running server uses
app.instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'instance')

with app.app_context():
    admin = Staff.query.filter_by(role=StaffRole.SUPER_ADMIN).first()
    if not admin:
        print("No super admin found in database.")
        sys.exit(1)

    print(f"Super admin found: {admin.email}")
    new_email = input("New email (press Enter to keep current): ").strip()
    new_password = input("New password (min 8 chars): ").strip()

    if not new_password or len(new_password) < 8:
        print("Password too short. Aborted.")
        sys.exit(1)

    if new_email:
        admin.email = new_email.lower()

    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    admin.password_hash = hashed.decode('utf-8')
    admin.must_change_password = False
    db.session.commit()

    print(f"\nDone. Login with:")
    print(f"  Email:    {admin.email}")
    print(f"  Password: {new_password}")
