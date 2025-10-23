from flask import current_app
import smtplib
from email.mime.text import MIMEText

def send_mail(to_email, subject, message):
    """Send email using app config values."""
    try:
        sender = current_app.config['EMAIL_USER']
        password = current_app.config['EMAIL_PASS']
        host = current_app.config['EMAIL_HOST']
        port = current_app.config['EMAIL_PORT']

        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = to_email

        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, [to_email], msg.as_string())

        print(f"✅ Email sent to {to_email}")
        return True

    except Exception as e:
        print(f"❌ Email send failed to {to_email}: {e}")
        return False
