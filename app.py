import os
import re
import threading
import sqlite3
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash


# =========================
# App Config
# =========================
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-in-production-very-strong-secret-key")

DB_NAME = os.environ.get("DB_NAME", "shubham_hospital3.db")

DEFAULT_ADMIN_EMAIL = os.environ.get("DEFAULT_ADMIN_EMAIL", "sadigaleshubham8@gmail.com")
DEFAULT_ADMIN_PASSWORD = os.environ.get("DEFAULT_ADMIN_PASSWORD", "ChangeAdminPassword123!")

ALLOWED_STATUSES = {"Pending", "Approved", "Cancelled"}


# =========================
# Helpers
# =========================
def get_db_connection():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def is_valid_email(email):
    if not email:
        return False
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(pattern, email) is not None


def is_valid_phone(number):
    if not number:
        return False
    cleaned = re.sub(r"[^\d]", "", number)
    return 10 <= len(cleaned) <= 15


def is_strong_password(password):
    return len(password) >= 8


def is_valid_date(date_text):
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_valid_time(time_text):
    if not time_text:
        return False

    time_text = time_text.strip()

    for fmt in ("%I:%M %p", "%H:%M", "%H:%M:%S"):
        try:
            datetime.strptime(time_text, fmt)
            return True
        except ValueError:
            continue

    return False


def safe_strip(value):
    return (value or "").strip()


def send_email(to_email, subject, body):
    try:
        sender_email = os.environ.get("SENDER_EMAIL")
        sender_password = os.environ.get("SENDER_PASSWORD")

        if not sender_email or not sender_password:
            print("❌ Email credentials missing.")
            return

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = to_email

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print("✅ Email sent to", to_email)

    except Exception as e:
        print("❌ Email error:", e)


def send_email_async(to_email, subject, body):
    thread = threading.Thread(target=send_email, args=(to_email, subject, body), daemon=True)
    thread.start()


# =========================
# Database Init
# =========================
def init_db():
    with sqlite3.connect(DB_NAME, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                number TEXT NOT NULL,
                password TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                number TEXT NOT NULL,
                message TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL,
                email TEXT NOT NULL,
                number TEXT NOT NULL,
                doctor TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                appointment_type TEXT NOT NULL,
                notes TEXT,
                status TEXT NOT NULL DEFAULT 'Pending'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fullname TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)

        cursor.execute("SELECT id FROM admins WHERE email = ?", (DEFAULT_ADMIN_EMAIL.strip().lower(),))
        admin = cursor.fetchone()

        if admin is None and DEFAULT_ADMIN_EMAIL and DEFAULT_ADMIN_PASSWORD:
            cursor.execute(
                "INSERT INTO admins (fullname, email, password) VALUES (?, ?, ?)",
                (
                    "Default Admin",
                    DEFAULT_ADMIN_EMAIL.strip().lower(),
                    generate_password_hash(DEFAULT_ADMIN_PASSWORD),
                ),
            )

        conn.commit()


# =========================
# Public Routes
# =========================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/home")
def main():
    return redirect(url_for("home"))


@app.route("/aboutus")
def about_us():
    return render_template("aboutus.html")


@app.route("/doctors")
def doctors():
    return render_template("doctor.html")


@app.route("/appointments", methods=["GET", "POST"])
def appointments():
    if request.method == "POST":
        data = {
            "firstname": safe_strip(request.form.get("firstname")),
            "lastname": safe_strip(request.form.get("lastname")),
            "email": safe_strip(request.form.get("email")).lower(),
            "number": safe_strip(request.form.get("number")),
            "doctor": safe_strip(request.form.get("doctor")),
            "date": safe_strip(request.form.get("date")),
            "time": safe_strip(request.form.get("time")),
            "appointment_type": safe_strip(request.form.get("type")),
            "notes": safe_strip(request.form.get("notes")),
            "status": "Pending",
        }

        if not all([
            data["firstname"], data["lastname"], data["email"], data["number"],
            data["doctor"], data["date"], data["time"], data["appointment_type"]
        ]):
            flash("Please fill all required appointment fields.", "error")
            return redirect(url_for("appointments"))

        if not is_valid_email(data["email"]):
            flash("Invalid email address.", "error")
            return redirect(url_for("appointments"))

        if not is_valid_phone(data["number"]):
            flash("Invalid phone number.", "error")
            return redirect(url_for("appointments"))

        if not is_valid_date(data["date"]):
            flash("Invalid appointment date.", "error")
            return redirect(url_for("appointments"))

        if not is_valid_time(data["time"]):
            flash("Invalid appointment time.", "error")
            return redirect(url_for("appointments"))

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO appointments
                    (firstname, lastname, email, number, doctor, date, time, appointment_type, notes, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data["firstname"],
                    data["lastname"],
                    data["email"],
                    data["number"],
                    data["doctor"],
                    data["date"],
                    data["time"],
                    data["appointment_type"],
                    data["notes"],
                    data["status"],
                ))
                conn.commit()

        except sqlite3.Error as e:
            print("Appointment DB error:", e)
            flash("Something went wrong while booking appointment.", "error")
            return redirect(url_for("appointments"))

        subject = "📅 Appointment Request Received - LifeCare Clinic"
        body = f"""Hello {data['firstname']} {data['lastname']},

Your appointment request has been received.

Doctor: {data['doctor']}
Date: {data['date']}
Time: {data['time']}
Appointment Type: {data['appointment_type']}

Status: Pending

Our admin will review your request shortly.

Thank you,
LifeCare Clinic
"""
        send_email_async(data["email"], subject, body)

        flash("📅 Appointment request sent!", "appointment")
        return redirect(url_for("home"))

    return render_template("appointment.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        data = {
            "name": safe_strip(request.form.get("name")),
            "email": safe_strip(request.form.get("email")).lower(),
            "number": safe_strip(request.form.get("number")),
            "message": safe_strip(request.form.get("message"))
        }

        if not all([data["name"], data["email"], data["number"], data["message"]]):
            flash("Please fill all fields.", "error")
            return redirect(url_for("contact"))

        if not is_valid_email(data["email"]):
            flash("Invalid email address.", "error")
            return redirect(url_for("contact"))

        if not is_valid_phone(data["number"]):
            flash("Invalid phone number.", "error")
            return redirect(url_for("contact"))

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO messages (name, email, number, message)
                    VALUES (?, ?, ?, ?)
                """, (
                    data["name"],
                    data["email"],
                    data["number"],
                    data["message"]
                ))
                conn.commit()

        except sqlite3.Error as e:
            print("Contact DB error:", e)
            flash("Something went wrong while sending message.", "error")
            return redirect(url_for("contact"))

        flash("📤 Message successfully sent!", "message")
        return redirect(url_for("contact"))

    return render_template("contact.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = safe_strip(request.form.get("email")).lower()
        password = safe_strip(request.form.get("password"))

        if not email or not password:
            flash("Please fill all fields.", "error")
            return redirect(url_for("login"))

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name, password FROM users WHERE email = ?", (email,))
                user = cursor.fetchone()

            if user and check_password_hash(user["password"], password):
                session.clear()
                session["user"] = user["name"]
                flash("✅ Login successful!", "success")
                return redirect(url_for("home"))

            flash("❌ Invalid credentials", "error")
            return redirect(url_for("login"))

        except sqlite3.Error as e:
            print("Login DB error:", e)
            flash("Login failed. Please try again.", "error")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = safe_strip(request.form.get("name"))
        email = safe_strip(request.form.get("email")).lower()
        number = safe_strip(request.form.get("number"))
        raw_password = safe_strip(request.form.get("password"))

        if not name or not email or not number or not raw_password:
            flash("Please fill all fields.", "error")
            return redirect(url_for("signup"))

        if not is_valid_email(email):
            flash("Invalid email address.", "error")
            return redirect(url_for("signup"))

        if not is_valid_phone(number):
            flash("Invalid phone number.", "error")
            return redirect(url_for("signup"))

        if not is_strong_password(raw_password):
            flash("Password must be at least 8 characters.", "error")
            return redirect(url_for("signup"))

        password = generate_password_hash(raw_password)

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (name, email, number, password) VALUES (?, ?, ?, ?)",
                    (name, email, number, password)
                )
                conn.commit()

            flash("👤 Account created!", "account")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("Email already registered.", "error")
            return redirect(url_for("signup"))

        except sqlite3.Error as e:
            print("Signup DB error:", e)
            flash("Something went wrong during signup. Please try again.", "error")
            return redirect(url_for("signup"))

    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    return render_template("logout.html")


# =========================
# Admin Routes
# =========================
@app.route("/dashboard")
def dashboard():
    if not session.get("admin_logged_in"):
        flash("⚠️ Admin login required", "error")
        return redirect(url_for("admin_login"))

    search = safe_strip(request.args.get("search"))

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            if search:
                cursor.execute("""
                    SELECT * FROM appointments
                    WHERE firstname LIKE ?
                       OR lastname LIKE ?
                       OR doctor LIKE ?
                       OR date LIKE ?
                    ORDER BY date DESC, time ASC
                """, (f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"))
            else:
                cursor.execute("SELECT * FROM appointments ORDER BY date DESC, time ASC")

            appointments_data = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) AS count FROM appointments")
            total = cursor.fetchone()["count"]

            cursor.execute("SELECT COUNT(*) AS count FROM appointments WHERE status='Pending'")
            pending = cursor.fetchone()["count"]

            cursor.execute("SELECT COUNT(*) AS count FROM appointments WHERE status='Approved'")
            approved = cursor.fetchone()["count"]

            cursor.execute("SELECT COUNT(*) AS count FROM appointments WHERE status='Cancelled'")
            cancelled = cursor.fetchone()["count"]

        return render_template(
            "dashboard.html",
            appointments=appointments_data,
            total=total,
            pending=pending,
            approved=approved,
            cancelled=cancelled,
            search=search
        )

    except sqlite3.Error as e:
        print("Dashboard DB error:", e)
        flash("Unable to load dashboard.", "error")
        return redirect(url_for("admin_login"))


@app.route("/dashboard/messages")
def messages():
    if not session.get("admin_logged_in"):
        flash("⛔ Admin access required", "m-error")
        return redirect(url_for("admin_login"))

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM messages ORDER BY id DESC")
            all_messages = cursor.fetchall()

        return render_template("messages.html", messages=all_messages)

    except sqlite3.Error as e:
        print("Messages DB error:", e)
        flash("Unable to load messages.", "m-error")
        return redirect(url_for("dashboard"))


@app.route("/dashboard/adddoctor")
def adddoctor():
    if not session.get("admin_logged_in"):
        flash("⛔ Admin access required", "m-error")
        return redirect(url_for("admin_login"))

    return render_template("adddoctor.html")


@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = safe_strip(request.form.get("email")).lower()
        password = safe_strip(request.form.get("password"))

        if not email or not password:
            flash("Please fill all fields.", "in-error")
            return redirect(url_for("admin_login"))

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT fullname, email, password FROM admins WHERE email = ?", (email,))
                admin = cursor.fetchone()

            if admin and check_password_hash(admin["password"], password):
                session.clear()
                session["admin_logged_in"] = True
                session["admin_email"] = admin["email"]
                session["admin_name"] = admin["fullname"]
                flash("✅ Admin login successful!", "in-success")
                return redirect(url_for("dashboard"))

            flash("❌ Invalid admin credentials", "in-error")
            return redirect(url_for("admin_login"))

        except sqlite3.Error as e:
            print("Admin login DB error:", e)
            flash("❌ Admin login failed.", "in-error")
            return redirect(url_for("admin_login"))

    return render_template("admin-login.html")


@app.route("/admin-signup", methods=["GET", "POST"])
def admin_signup():
    if request.method == "POST":
        fullname = safe_strip(request.form.get("fullname"))
        email = safe_strip(request.form.get("email")).lower()
        raw_password = safe_strip(request.form.get("password"))

        if not fullname or not email or not raw_password:
            flash("Please fill all fields.", "up-error")
            return redirect(url_for("admin_signup"))

        if not is_valid_email(email):
            flash("Invalid email address.", "up-error")
            return redirect(url_for("admin_signup"))

        if not is_strong_password(raw_password):
            flash("Password must be at least 8 characters.", "up-error")
            return redirect(url_for("admin_signup"))

        password = generate_password_hash(raw_password)

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO admins (fullname, email, password) VALUES (?, ?, ?)",
                    (fullname, email, password)
                )
                conn.commit()

            flash("✅ Admin account created!", "up-success")
            return redirect(url_for("admin_login"))

        except sqlite3.IntegrityError:
            flash("❌ Admin email already registered!", "up-error")
            return redirect(url_for("admin_signup"))

        except sqlite3.Error as e:
            print("Admin signup DB error:", e)
            flash("❌ Something went wrong during admin signup.", "up-error")
            return redirect(url_for("admin_signup"))

    return render_template("admin-signup.html")


@app.route("/admin-logout")
def admin_logout():
    session.clear()
    flash("🔐 Logged out from Admin.", "info")
    return redirect(url_for("admin_login"))


@app.route("/update_status/<int:id>", methods=["POST"])
def update_status(id):
    if not session.get("admin_logged_in"):
        flash("⚠️ Admin login required", "error")
        return redirect(url_for("admin_login"))

    new_status = safe_strip(request.form.get("status"))

    if new_status not in ALLOWED_STATUSES:
        flash("Invalid status selected.", "error")
        return redirect(url_for("dashboard"))

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM appointments WHERE id = ?", (id,))
            appointment = cursor.fetchone()

            if not appointment:
                flash("Appointment not found.", "error")
                return redirect(url_for("dashboard"))

            cursor.execute(
                "UPDATE appointments SET status = ? WHERE id = ?",
                (new_status, id)
            )
            conn.commit()

        email = appointment["email"]

        if email:
            if new_status == "Approved":
                subject = "✅ Appointment Approved - LifeCare Clinic"
                body = f"""Hello {appointment['firstname']} {appointment['lastname']},

Your appointment has been approved.

Doctor: {appointment['doctor']}
Date: {appointment['date']}
Time: {appointment['time']}
Status: {new_status}

Thank you,
LifeCare Clinic
"""
                send_email_async(email, subject, body)

            elif new_status == "Cancelled":
                subject = "❌ Appointment Cancelled - LifeCare Clinic"
                body = f"""Hello {appointment['firstname']} {appointment['lastname']},

Your appointment has been cancelled.

Doctor: {appointment['doctor']}
Date: {appointment['date']}
Time: {appointment['time']}
Status: {new_status}

Thank you,
LifeCare Clinic
"""
                send_email_async(email, subject, body)

        flash("Status updated", "s-updated")
        return redirect(url_for("dashboard"))

    except sqlite3.Error as e:
        print("Update status DB error:", e)
        flash("Could not update status.", "error")
        return redirect(url_for("dashboard"))


@app.route("/delete_appointment/<int:id>", methods=["POST"])
def delete_appointment(id):
    if not session.get("admin_logged_in"):
        flash("⚠️ Admin login required", "error")
        return redirect(url_for("admin_login"))

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM appointments WHERE id = ?", (id,))
            appointment = cursor.fetchone()

            if not appointment:
                flash("Appointment not found.", "error")
                return redirect(url_for("dashboard"))

            cursor.execute("DELETE FROM appointments WHERE id = ?", (id,))
            conn.commit()

        flash("Appointment deleted", "s-deleted")
        return redirect(url_for("dashboard"))

    except sqlite3.Error as e:
        print("Delete appointment DB error:", e)
        flash("Could not delete appointment.", "error")
        return redirect(url_for("dashboard"))


# =========================
# Start App
# =========================
init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=False)
