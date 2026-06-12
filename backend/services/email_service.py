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
        # Dev mode: write to stdout safely on Windows (cp1252 can't handle emojis)
        msg = f"\n[EMAIL DEV MODE]\nTo: {to_email}\nSubject: {subject}\n"
        import sys
        sys.stdout.buffer.write(msg.encode('utf-8', errors='replace') + b"\n")
        sys.stdout.flush()
        return True

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = to_email
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        with smtplib.SMTP(mail_server, mail_port) as server:
            server.starttls()
            server.login(mail_user, mail_pass)
            server.sendmail(mail_user, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False

def send_welcome_email(to_email: str, first_name: str):
    subject = "Welcome to Airfinder ✈"
    body = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:auto;">
      <h2 style="color:#407E3C;">Welcome to Airfinder, {first_name}!</h2>
      <p>Your account is ready. Start searching for the best flights worldwide — with full price transparency.</p>
      <a href="http://localhost:5000" style="background:#407E3C;color:white;padding:12px 24px;text-decoration:none;border-radius:6px;display:inline-block;margin-top:16px;">Search Flights</a>
      <p style="color:#888;margin-top:32px;font-size:12px;">Airfinder — Fly Smart, Pay Fair</p>
    </div>
    """
    send_email(to_email, subject, body)

def send_password_reset_email(to_email: str, first_name: str, reset_link: str):
    subject = "Reset Your Airfinder Password"
    body = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:auto;">
      <h2 style="color:#407E3C;">Password Reset Request</h2>
      <p>Hi {first_name}, we received a request to reset your Airfinder password.</p>
      <a href="{reset_link}" style="background:#407E3C;color:white;padding:12px 24px;text-decoration:none;border-radius:6px;display:inline-block;margin-top:16px;">Reset Password</a>
      <p style="color:#888;margin-top:16px;">This link expires in 15 minutes. If you didn't request this, ignore this email.</p>
    </div>
    """
    send_email(to_email, subject, body)

def send_staff_credentials_email(to_email: str, first_name: str, role: str, temp_password: str):
    subject = "Your Airfinder Staff Account"
    body = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:auto;">
      <h2 style="color:#407E3C;">Welcome to the Airfinder Team, {first_name}!</h2>
      <p>Your staff account has been created with the role: <strong>{role.replace('_', ' ').title()}</strong></p>
      <div style="background:#f5f5f5;padding:16px;border-radius:8px;margin:16px 0;">
        <p style="margin:4px 0;"><strong>Email:</strong> {to_email}</p>
        <p style="margin:4px 0;"><strong>Temporary Password:</strong> <code style="background:#e0e0e0;padding:2px 6px;border-radius:4px;">{temp_password}</code></p>
      </div>
      <p style="color:#d32f2f;"><strong>You must change this password on first login.</strong></p>
      <a href="http://localhost:5000/admin/login" style="background:#407E3C;color:white;padding:12px 24px;text-decoration:none;border-radius:6px;display:inline-block;margin-top:16px;">Login to Staff Portal</a>
    </div>
    """
    send_email(to_email, subject, body)

def send_booking_confirmation_email(to_email: str, first_name: str, booking: dict):
    subject = f"Booking Confirmed — {booking.get('reference', '')}"
    body = f"""
    <div style="font-family:sans-serif;max-width:600px;margin:auto;">
      <h2 style="color:#407E3C;">Booking Confirmed ✓</h2>
      <p>Hi {first_name}, your flight has been booked successfully.</p>
      <div style="background:#f5f5f5;padding:16px;border-radius:8px;margin:16px 0;">
        <p><strong>Reference:</strong> {booking.get('reference')}</p>
        <p><strong>Route:</strong> {booking.get('origin')} → {booking.get('destination')}</p>
        <p><strong>Date:</strong> {booking.get('departure_date')}</p>
        <p><strong>Airline:</strong> {booking.get('airline')}</p>
        <p><strong>Total Paid:</strong> ${booking.get('pricing', {}).get('total', 0)}</p>
      </div>
      <p style="color:#888;margin-top:32px;font-size:12px;">Airfinder — Fly Smart, Pay Fair</p>
    </div>
    """
    send_email(to_email, subject, body)
