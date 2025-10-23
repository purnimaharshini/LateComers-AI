    
#      🕒 Latecomers Attendance Management System

An intelligent, AI-enhanced web platform built with **Flask (Python)** that automates tracking of late student arrivals, improves teacher productivity, and strengthens parent-school communication through **real-time notifications and analytics dashboards**.

---

## 🚀 Features:

### 👩‍🏫 Teacher Dashboard
- Mark late students (single or bulk selection)
- Add reasons for lateness  
- Visualize daily and weekly attendance trends with interactive charts  
- See **AI-powered punctuality insights** (e.g., "Late arrivals dropped by 20% this week")  
- Identify **repeat offenders** (students late multiple times this week)
- Quick filtering by class or student name  

### 👨‍🎓 Student Dashboard
- View personal late arrival records  
- Track dates, times, and reasons of lateness  
- Simple and student-friendly UI  

### 🧑‍💼 Admin Dashboard
- Analyze lateness data across classes  
- Export reports in **CSV or PDF formats**  
- Access **AI-generated risk reports** identifying high-risk students  
- View late reasons distribution and trends  
- Receive **AI-driven suggestions** for attendance improvement  

### 📬 Notifications
- Automated **email alerts** to parents when a student is marked late  
- (Optional) Can be extended with **SMS notifications**  

### 🧠 AI Analytics
- Machine-learning–based lateness risk prediction  
- AI-generated insights and attendance summaries  

---

## 🛠️ Tech Stack

| Category | Technology |
|-----------|-------------|
| Backend | Python, Flask, SQLAlchemy |
| Frontend | HTML5, CSS3, Bootstrap 5, Plotly.js |
| Database | SQLite |
| Authentication | Flask-Login, bcrypt |
| Notifications | SMTP (Email), SMS Gateway (optional) |
| AI Utils | Python (Custom logic & ML integration) |

---

## ⚙️ Installation & Setup:

### 1️⃣ Clone the repository
```bash
git clone https://github.com/purnimaharshini/latecomers_web.git
cd latecomers_web


2️⃣ Create a virtual environment
python -m venv venv
venv\Scripts\activate  # (on Windows)

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Set up environment variables (.env)
SECRET_KEY=your_secret_key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_USE_TLS=True

5️⃣ Run the application
python app.py


Visit 👉 http://127.0.0.1:5000

👩‍🏫 Teacher View:

Daily and weekly late trend charts

Repeat offenders list

Quick search and filter tools

🧑‍💼 Admin View:

Class-wise risk ranking

Late reason analysis

Export tools for reports (CSV, PDF)

💡 Future Enhancements:

SMS notifications to parents

Mobile-friendly PWA design

Attendance prediction using ML

Student profile performance integration



🧑‍💻 Author

Purnima Harshini
B.Tech – Final Year (2026 Batch)
📍 Passionate about AI-driven educational tools and full-stack development

## 🎥 Demo Video & Screenshots

### 🎬 Project Walkthrough (Demo Video)
🔗 [Watch Demo on YouTube](https://youtu.be/your-demo-link)  
*(Upload your screen recording — even a 2–3 min walkthrough showing teacher, student, and admin views is perfect.)*

### 🖼️ Screenshots

| Dashboard | Description |
|------------|-------------|
| ![Teacher Dashboard]     (static/images/teacher_dashboard.png) | Teacher can mark students late, view trends & repeat offenders |
| ![Admin Dashboard]       (static/images/admin_dashboard.png) | Admin can analyze lateness data, generate AI risk reports & export |
| ![Student Dashboard]     (static/images/student_dashboard.png) | Students can track their own attendance & lateness history |
| ![Login Page]            (static/images/login_page.png) | Simple and secure login interface |

🧾 License

This project is open-source and available for educational and portfolio use.