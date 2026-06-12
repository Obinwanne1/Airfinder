from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, inspect as sa_inspect

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    with app.app_context():
        from backend.models import user, staff, booking  # noqa: F401
        db.create_all()
        _migrate_existing(app)
        _seed_super_admin(app)

def _migrate_existing(app):
    """Add columns introduced after initial schema without dropping data."""
    inspector = sa_inspect(db.engine)
    if 'bookings' not in inspector.get_table_names():
        return
    existing = {c['name'] for c in inspector.get_columns('bookings')}
    additions = []
    if 'group_reference' not in existing:
        additions.append('ALTER TABLE bookings ADD COLUMN group_reference VARCHAR(20)')
    if 'is_multicity' not in existing:
        additions.append('ALTER TABLE bookings ADD COLUMN is_multicity BOOLEAN DEFAULT 0')
    if additions:
        with db.engine.connect() as conn:
            for stmt in additions:
                conn.execute(text(stmt))
            conn.commit()

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
