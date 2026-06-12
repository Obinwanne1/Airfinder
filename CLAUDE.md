# Airfinder — Project Notes

## Stack
- Backend: Python + Flask (port 5000)
- DB: SQLite (airfinder.db) via SQLAlchemy
- Auth: JWT + bcrypt
- Frontend: Vanilla HTML/CSS/JS in /frontend/

## Run
```
python backend/app.py
```

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
- POST /api/bookings — create booking (auth required)
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
