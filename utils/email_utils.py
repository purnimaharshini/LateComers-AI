def send_email():
    try:
        sender = os.getenv("EMAIL_USER")
        password = os.getenv("EMAIL_PASS")
        if not sender or not password:
            print("⚠ Email not configured, skipping send.")
            return
        # ... rest of send logic
    except Exception as e:
        print(f"❌ Email send failed: {e}")
