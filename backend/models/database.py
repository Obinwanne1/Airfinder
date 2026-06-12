from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    with app.app_context():
        # Import all models so SQLAlchemy registers their tables before create_all
        from backend.models import user, staff, booking  # noqa: F401
        db.create_all()
        _seed_super_admin(app)

def _seed_super_admin(app):
    from backend.models.staff import Staff, StaffRole
    from backend.config import Config
    import bcrypt

    existing = Staff.query.filter_by(email=Config.SUPER_ADMIN_EMAIL).first()
    if existing:
        return

    hashed = bcrypt.hashpw(Config.SUPER_ADMIN_PASSWORD.encode('utf-8'), bcrypt.gensalt())
    super_admin = Staff(
        email=Config.SUPER_ADMIN_EMAIL,
        password_hash=hashed.decode('utf-8'),
        first_name='Super',
        last_name='Admin',
        role=StaffRole.SUPER_ADMIN,
        must_change_password=False,
        is_active=True
    )
    db.session.add(super_admin)
    db.session.commit()
    print(f"[SEED] Super admin created: {Config.SUPER_ADMIN_EMAIL}")
