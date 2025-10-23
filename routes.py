from flask import render_template, request, redirect, url_for, flash, Response
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import text
from datetime import datetime
from io import StringIO, BytesIO
import csv
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import utils.ai_utils as ai_utils
from app import app, db, bcrypt, login_manager
from models import User, LateRecord, SchoolRecord
import utils.email_utils as email_utils
import utils.sms_utils as sms_utils

# Serializer for password reset tokens
serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------- Index ----------
@app.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return redirect(url_for("admin_dashboard"))
        elif current_user.role == "teacher":
            return redirect(url_for("teacher_dashboard"))
        else:
            return redirect(url_for("student_dashboard"))
    return redirect(url_for("login"))

# ---------- Auth ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful", "success")

            if user.role == "admin":
                return redirect(url_for("admin_dashboard"))
            elif user.role == "teacher":
                return redirect(url_for("teacher_dashboard"))
            else:
                return redirect(url_for("student_dashboard"))
        else:
            flash("Invalid username or password", "danger")

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "info")
    return redirect(url_for("login"))

# ---------- Forgot Password ----------
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(username=email).first()  # assuming username=email
        if user:
            token = serializer.dumps(email, salt="password-reset-salt")
            reset_link = url_for("reset_password", token=token, _external=True)
            subject = "Password Reset Request"
            message = f"Hello,\n\nClick the link below to reset your password:\n{reset_link}\n\nIf you didn’t request this, please ignore."
            email_utils.send_mail(email, subject, message)
            flash("Reset link sent to your email.", "info")
        else:
            flash("No account found with that email.", "danger")
    return render_template("forgot_password.html")

# ---------- Reset Password ----------
@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        email = serializer.loads(token, salt="password-reset-salt", max_age=3600)
    except SignatureExpired:
        flash("The reset link has expired.", "danger")
        return redirect(url_for("forgot_password"))
    except BadSignature:
        flash("Invalid reset token.", "danger")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        new_password = request.form.get("password")
        user = User.query.filter_by(username=email).first()
        if user:
            hashed_pw = bcrypt.generate_password_hash(new_password).decode("utf-8")
            user.password = hashed_pw
            db.session.commit()
            flash("Password reset successful. You can now log in.", "success")
            return redirect(url_for("login"))
        else:
            flash("User not found.", "danger")

    return render_template("reset_password.html")

# ---------- Dashboard ----------
@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "admin":
        return redirect(url_for("admin_dashboard"))
    elif current_user.role == "teacher":
        return redirect(url_for("teacher_dashboard"))
    else:
        return redirect(url_for("student_dashboard"))

# ---------- Teacher ----------
from datetime import date, timedelta
from sqlalchemy import func

@app.route("/teacher")
@login_required
def teacher_dashboard():
    if current_user.role != "teacher":
        return redirect(url_for("login"))

    students = SchoolRecord.query.order_by(SchoolRecord.student_name).all()
    recent = LateRecord.query.order_by(LateRecord.date.desc()).limit(20).all()

    # --- Summary Counts ---
    today = date.today()
    yesterday = today - timedelta(days=1)
    day_before_yesterday = today - timedelta(days=2)

    today_count = LateRecord.query.filter_by(marked_by=current_user.id, date=today).count()
    yesterday_count = LateRecord.query.filter_by(marked_by=current_user.id, date=yesterday).count()
    day_before_yesterday_count = LateRecord.query.filter_by(marked_by=current_user.id, date=day_before_yesterday).count()

    today_records = LateRecord.query.filter_by(marked_by=current_user.id, date=today).all()

    # --- Weekly Trend ---
    week_ago = today - timedelta(days=6)
    trend_data = (
        db.session.query(LateRecord.date, func.count(LateRecord.id))
        .filter(LateRecord.marked_by == current_user.id, LateRecord.date >= week_ago)
        .group_by(LateRecord.date)
        .order_by(LateRecord.date)
        .all()
    )

    dates = [str(r[0]) for r in trend_data]
    counts = [r[1] for r in trend_data]

    # --- AI Insights ---
    if len(counts) >= 2:
        avg_recent = sum(counts[-3:]) / min(3, len(counts))
        avg_past = sum(counts[:-3]) / max(1, len(counts[:-3])) if len(counts) > 3 else avg_recent
        diff = avg_recent - avg_past

        if diff < 0:
            ai_message = f"✅ Great work! Late arrivals dropped by {abs(int((diff / avg_past) * 100)) if avg_past else 0}% compared to earlier days."
            ai_color = "success"
        elif diff > 0:
            ai_message = f"⚠ Late arrivals increased by {int((diff / avg_past) * 100) if avg_past else diff}% this week — monitor punctuality."
            ai_color = "warning"
        else:
            ai_message = "ℹ Attendance trend is stable this week."
            ai_color = "info"
    else:
        ai_message = "📊 Not enough data yet to generate insights."
        ai_color = "secondary"

    # --- Repeat Offenders (This Week) ---
    week_start = today - timedelta(days=7)
    repeat_offenders = (
        db.session.query(LateRecord.student_name, func.count(LateRecord.id).label("late_count"))
        .filter(LateRecord.marked_by == current_user.id, LateRecord.date >= week_start)
        .group_by(LateRecord.student_name)
        .having(func.count(LateRecord.id) > 1)
        .order_by(func.count(LateRecord.id).desc())
        .limit(5)
        .all()
    )

    return render_template(
        "teacher_dashboard.html",
        students=students,
        recent=recent,
        today_count=today_count,
        yesterday_count=yesterday_count,
        day_before_yesterday_count=day_before_yesterday_count,
        today_records=today_records,
        dates=dates,
        counts=counts,
        ai_message=ai_message,
        ai_color=ai_color,
        repeat_offenders=repeat_offenders,
    )


@app.route("/mark_late", methods=["POST"])
@login_required
def mark_late():
    if current_user.role != "teacher":
        return redirect(url_for("login"))

    adm = request.form.get("admission_no")
    reason = request.form.get("reason", "").strip() or "Not specified"
    now = datetime.now()

    if not adm:
        flash("No student selected!", "danger")
        return redirect(url_for("teacher_dashboard"))

    lr = LateRecord(
        admission_no=adm,
        student_name="",
        date=now.date(),
        time=now.time(),
        reason=reason,
        marked_by=current_user.id
    )

    student = SchoolRecord.query.filter_by(admission_no=adm).first()
    if student:
        lr.student_name = student.student_name

    db.session.add(lr)
    db.session.commit()

    # Send notification
    if student and student.parent_email:
        subject = "Late Arrival Notice"
        body = (
            f"Dear Parent,\n\nYour child {student.student_name} (Adm {adm}) "
            f"was late on {now.date()} at {now.time().strftime('%H:%M:%S')}. "
            f"Reason: {reason}.\n\nRegards,\nSchool Administration"
        )
        email_utils.send_mail(student.parent_email, subject, body)

    flash("Late record saved.", "success")
    return redirect(url_for("teacher_dashboard"))

@app.route("/mark_late_bulk", methods=["POST"])
@login_required
def mark_late_bulk():
    if current_user.role != "teacher":
        return redirect(url_for("login"))

    selected = request.form.getlist("selected_students")
    reason = request.form.get("reason", "").strip() or "Not specified"
    now = datetime.now()

    if not selected:
        flash("No students selected!", "warning")
        return redirect(url_for("teacher_dashboard"))

    for adm in selected:
        student = SchoolRecord.query.filter_by(admission_no=adm).first()
        if student:
            lr = LateRecord(
                admission_no=adm,
                student_name=student.student_name,
                date=now.date(),
                time=now.time(),
                reason=reason,
                marked_by=current_user.id
            )
            db.session.add(lr)

            # Optional: Notify parent
            if student.parent_email:
                subject = "Late Arrival Notice"
                body = (
                    f"Dear Parent,\n\nYour child {student.student_name} (Adm {adm}) "
                    f"was marked late on {now.date()} at {now.time().strftime('%H:%M:%S')}.\n"
                    f"Reason: {reason}.\n\nRegards,\nSchool Administration"
                )
                email_utils.send_mail(student.parent_email, subject, body)

    db.session.commit()
    flash(f"{len(selected)} students marked as late.", "success")
    return redirect(url_for("teacher_dashboard"))


# ---------- Student ----------
@app.route("/student")
@login_required
def student_dashboard():
    if current_user.role != "student":
        return redirect(url_for("login"))

    adm = current_user.admission_no

    # --- Records for Table ---
    records = (
        LateRecord.query
        .filter_by(admission_no=adm)
        .order_by(LateRecord.date.desc())
        .all()
    )

    # --- Summary Stats ---
    total_late = len(records)
    month_start = date.today().replace(day=1)
    late_this_month = LateRecord.query.filter(
        LateRecord.admission_no == adm, LateRecord.date >= month_start
    ).count()

    # Find the student’s best on-time streak
    streak = 0
    current_streak = 0
    last_date = None
    all_dates = sorted([r.date for r in records])
    for d in all_dates:
        if last_date and (d - last_date).days == 1:
            current_streak += 1
        else:
            streak = max(streak, current_streak)
            current_streak = 1
        last_date = d
    best_streak = max(streak, current_streak)

    # --- AI-style Message ---
    if late_this_month == 0:
        ai_message = "🌟 Perfect punctuality this month — keep it up!"
        ai_color = "success"
    elif late_this_month <= 2:
        ai_message = "⚠ Good job, but aim for a perfect month next time!"
        ai_color = "warning"
    else:
        ai_message = "❗Frequent lateness detected — try improving your morning routine."
        ai_color = "danger"

    # --- Trend Data for Plotly ---
    trend_data = (
        db.session.query(LateRecord.date, func.count(LateRecord.id))
        .filter(LateRecord.admission_no == adm)
        .group_by(LateRecord.date)
        .order_by(LateRecord.date)
        .all()
    )
    dates = [str(r[0]) for r in trend_data]
    counts = [r[1] for r in trend_data]

    # --- Motivational Tip ---
    import random
    tips = [
        "⏰ Being 5 minutes early is better than being 1 minute late!",
        "🎯 Consistency builds character. Keep showing up!",
        "💪 Great work starts with great discipline.",
        "🚀 Start your day strong — success follows effort!",
    ]
    daily_tip = random.choice(tips)

    return render_template(
        "student_dashboard.html",
        records=records,
        total_late=total_late,
        late_this_month=late_this_month,
        best_streak=best_streak,
        ai_message=ai_message,
        ai_color=ai_color,
        dates=dates,
        counts=counts,
        daily_tip=daily_tip
    )

# ---------- Admin ----------
@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        return redirect(url_for("login"))

    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")
    class_filter = request.form.get("class_filter", "all")

    query = LateRecord.query.join(SchoolRecord, LateRecord.admission_no == SchoolRecord.admission_no)
    if start_date:
        query = query.filter(LateRecord.date >= start_date)
    if end_date:
        query = query.filter(LateRecord.date <= end_date)
    if class_filter != "all":
        query = query.filter(SchoolRecord.class_ == class_filter)

    late_records = query.order_by(LateRecord.date.desc(), LateRecord.time.desc()).all()

    # Top late students
    sql_top = text("""
        SELECT s.student_name, COUNT(*) as cnt
        FROM laterecords l
        JOIN schoolrecords s ON l.admission_no = s.admission_no
        GROUP BY l.admission_no
        ORDER BY cnt DESC LIMIT 10
    """)
    top_students = db.session.execute(sql_top).fetchall()

    # Late trends
    sql_trend = text("""
        SELECT l.date, COUNT(*) as cnt
        FROM laterecords l
        GROUP BY l.date ORDER BY l.date
    """)
    late_trends = db.session.execute(sql_trend).fetchall()

    # Reasons distribution
    sql_reason = text("""
        SELECT reason, COUNT(*) as cnt
        FROM laterecords GROUP BY reason
    """)
    reason_dist = db.session.execute(sql_reason).fetchall()

    # Class list
    classes = SchoolRecord.query.with_entities(SchoolRecord.class_).distinct().all()

    total_count = len(late_records)

    # AI risk prediction
    high_risk = ai_utils.train_and_predict_risk()

    # ---------- Summary counts ----------
    total_students = SchoolRecord.query.count()

    month_start = datetime.now().date().replace(day=1)
    total_late_month = LateRecord.query.filter(LateRecord.date >= month_start).count()

    high_risk_count = len(high_risk)

    sql_warn = text("""
        SELECT COUNT(DISTINCT l.admission_no) AS cnt
        FROM laterecords l
        JOIN schoolrecords s ON l.admission_no = s.admission_no
        WHERE l.date >= :month_ago
        GROUP BY l.admission_no
        HAVING COUNT(l.id) > 3
    """)
    warning_students_count = len(db.session.execute(sql_warn, {"month_ago": month_start}).fetchall())

    # ---------- Render Template ----------
    return render_template(
        "admin_dashboard.html",
        top_students=top_students,
        late_trends=late_trends,
        reason_dist=reason_dist,
        late_records=late_records,
        classes=classes,
        start_date=start_date,
        end_date=end_date,
        class_filter=class_filter,
        total_count=total_count,
        high_risk=high_risk,
        total_students=total_students,
        total_late_month=total_late_month,
        high_risk_count=high_risk_count,
        warning_students_count=warning_students_count
    )



@app.route('/export_csv', methods=['POST'])
@login_required
def export_csv():
    # Export latecomers data as CSV with filters
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")
    class_filter = request.form.get("class_filter", "all")

    query = LateRecord.query.join(SchoolRecord, LateRecord.admission_no == SchoolRecord.admission_no)
    if start_date:
        query = query.filter(LateRecord.date >= start_date)
    if end_date:
        query = query.filter(LateRecord.date <= end_date)
    if class_filter != "all":
        query = query.filter(SchoolRecord.class_ == class_filter)

    late_records = query.order_by(LateRecord.date.desc(), LateRecord.time.desc()).all()

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['Date', 'Time', 'Student Name', 'Admission No', 'Reason'])
    for lr in late_records:
        writer.writerow([
            lr.date,
            lr.time.strftime('%H:%M:%S'),
            lr.student_name,
            lr.admission_no,
            lr.reason
        ])
    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=latecomers.csv"}
    )
# ---------- AI-Driven Warning System for Admin ----------
from datetime import timedelta
import random

@app.route("/admin/warnings")
@login_required
def admin_warnings():
    if current_user.role != "admin":
        return redirect(url_for("login"))

    today = datetime.now().date()
    month_ago = today - timedelta(days=30)

    sql_warning = text("""
        SELECT s.student_name, s.class AS class_name, COUNT(l.id) AS late_count
        FROM laterecords l
        JOIN schoolrecords s ON l.admission_no = s.admission_no
        WHERE l.date >= :month_ago
        GROUP BY l.admission_no, s.student_name, s.class
        HAVING late_count > 3
        ORDER BY late_count DESC
    """)
    warning_students = db.session.execute(sql_warning, {"month_ago": month_ago}).fetchall()

    # Generate AI-style risk analysis
    risk_data = []
    for i, s in enumerate(warning_students, start=1):
        # simple AI logic (could be replaced with ML later)
        risk = min(100, s.late_count * 15 + random.randint(0, 10))
        if risk > 85:
            advice = "Immediate parent meeting recommended. Consider counselling for punctuality."
        elif risk > 60:
            advice = "Send weekly reminders and monitor attendance closely."
        else:
            advice = "Occasional lateness observed; encourage consistent routine."

        risk_data.append({
            "rank": i,
            "student_name": s.student_name,
            "class_name": s.class_name,
            "late_count": s.late_count,
            "risk": risk,
            "advice": advice
        })

    return render_template("admin_warnings.html", warning_students=risk_data)


@app.route('/export_pdf', methods=['POST'])
@login_required
def export_pdf():
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")
    class_filter = request.form.get("class_filter", "all")

    query = LateRecord.query.join(SchoolRecord, LateRecord.admission_no == SchoolRecord.admission_no)
    if start_date:
        query = query.filter(LateRecord.date >= start_date)
    if end_date:
        query = query.filter(LateRecord.date <= end_date)
    if class_filter != "all":
        query = query.filter(SchoolRecord.class_ == class_filter)

    late_records = query.order_by(LateRecord.date.desc(), LateRecord.time.desc()).all()

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 16)
    p.drawString(30, height - 40, "Latecomers Report")

    p.setFont("Helvetica", 12)
    y = height - 70
    p.drawString(30, y, "Date")
    p.drawString(100, y, "Time")
    p.drawString(170, y, "Student Name")
    p.drawString(350, y, "Admission No")
    p.drawString(450, y, "Reason")
    y -= 20

    for lr in late_records:
        if y < 40:
            p.showPage()
            y = height - 40
        p.drawString(30, y, str(lr.date))
        p.drawString(100, y, lr.time.strftime('%H:%M:%S'))
        p.drawString(170, y, lr.student_name)
        p.drawString(350, y, str(lr.admission_no))
        p.drawString(450, y, lr.reason)
        y -= 20

    p.save()
    buffer.seek(0)
    return Response(
        buffer,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment;filename=latecomers.pdf"}
    )
@app.route("/export_warnings_csv", methods=["POST"])
@login_required
def export_warnings_csv():
    today = datetime.now().date()
    month_ago = today - timedelta(days=30)

    sql_warning = text("""
        SELECT s.student_name, s.class AS class_name, COUNT(l.id) AS late_count
        FROM laterecords l
        JOIN schoolrecords s ON l.admission_no = s.admission_no
        WHERE l.date >= :month_ago
        GROUP BY l.admission_no, s.student_name, s.class
        HAVING late_count > 3
        ORDER BY late_count DESC
    """)
    records = db.session.execute(sql_warning, {"month_ago": month_ago}).fetchall()

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["Rank", "Student Name", "Class", "Late Count", "Risk %", "AI Advice"])

    for i, s in enumerate(records, start=1):
        risk = min(100, s.late_count * 15 + random.randint(0, 10))
        if risk > 85:
            advice = "Immediate parent meeting recommended."
        elif risk > 60:
            advice = "Send weekly reminders."
        else:
            advice = "Encourage consistency."
        writer.writerow([i, s.student_name, s.class_name, s.late_count, risk, advice])

    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=AI_Warnings_Report.csv"}
    )


@app.route("/export_warnings_pdf", methods=["POST"])
@login_required
def export_warnings_pdf():
    today = datetime.now().date()
    month_ago = today - timedelta(days=30)

    sql_warning = text("""
        SELECT s.student_name, s.class AS class_name, COUNT(l.id) AS late_count
        FROM laterecords l
        JOIN schoolrecords s ON l.admission_no = s.admission_no
        WHERE l.date >= :month_ago
        GROUP BY l.admission_no, s.student_name, s.class
        HAVING late_count > 3
        ORDER BY late_count DESC
    """)
    records = db.session.execute(sql_warning, {"month_ago": month_ago}).fetchall()

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 16)
    p.drawString(30, height - 40, "AI-Driven Latecomer Risk Report")

    y = height - 70
    p.setFont("Helvetica-Bold", 12)
    p.drawString(30, y, "Rank")
    p.drawString(70, y, "Student Name")
    p.drawString(250, y, "Class")
    p.drawString(320, y, "Late Count")
    p.drawString(420, y, "Risk %")
    y -= 20

    p.setFont("Helvetica", 10)
    for i, s in enumerate(records, start=1):
        risk = min(100, s.late_count * 15 + random.randint(0, 10))
        p.drawString(30, y, str(i))
        p.drawString(70, y, s.student_name)
        p.drawString(250, y, s.class_name)
        p.drawString(320, y, str(s.late_count))
        p.drawString(420, y, f"{risk}%")
        y -= 15
        if y < 40:
            p.showPage()
            y = height - 40

    p.save()
    buffer.seek(0)
    return Response(
        buffer,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment;filename=AI_Warnings_Report.pdf"}
    )
