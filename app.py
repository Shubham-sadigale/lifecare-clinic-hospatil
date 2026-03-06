import os
import threading
import sqlite3
import smtplib
from email.mime.text import MIMEText

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "shubham_secret_2026_123")

WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "shubham_webhook_2026_123")
DB_NAME = os.environ.get("DB_NAME", "shubham_hospital.db")

DEFAULT_ADMIN_EMAIL = os.environ.get("DEFAULT_ADMIN_EMAIL", "sadigaleshubham8@gmail.com")
DEFAULT_ADMIN_PASSWORD = os.environ.get("DEFAULT_ADMIN_PASSWORD", "admin123")


def get_db_connection():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with sqlite3.connect(DB_NAME, timeout=10) as conn:
        cursor = conn.cursor()

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
                message TEXT
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
                status TEXT DEFAULT 'Pending'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fullname TEXT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)

        cursor.execute("SELECT * FROM admins WHERE email = ?", (DEFAULT_ADMIN_EMAIL,))
        admin = cursor.fetchone()

        if admin is None:
            cursor.execute(
                "INSERT INTO admins (fullname, email, password) VALUES (?, ?, ?)",
                (
                    "Default Admin",
                    DEFAULT_ADMIN_EMAIL,
                    generate_password_hash(DEFAULT_ADMIN_PASSWORD),
                ),
            )

        conn.commit()


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
            "firstname": request.form.get("firstname", "").strip(),
            "lastname": request.form.get("lastname", "").strip(),
            "email": request.form.get("email", "").strip(),
            "number": request.form.get("number", "").strip(),
            "doctor": request.form.get("doctor", "").strip(),
            "date": request.form.get("date", "").strip(),
            "time": request.form.get("time", "").strip(),
            "appointment_type": request.form.get("type", "").strip(),
            "notes": request.form.get("notes", "").strip(),
            "status": "Pending",
        }

        conn = get_db_connection()
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
        conn.close()

        flash("📅 Appointment request sent!", "appointment")
        return redirect(url_for("home"))

    return render_template("appointment.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        data = {
            "name": request.form.get("name", "").strip(),
            "email": request.form.get("email", "").strip(),
            "number": request.form.get("number", "").strip(),
            "message": request.form.get("message", "").strip()
        }

        conn = get_db_connection()
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
        conn.close()

        flash("📤 Message successfully sent!", "message")
        return redirect(url_for("contact"))

    return render_template("contact.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user"] = user["name"]
            flash("✅ Login successful!", "success")
            return redirect(url_for("home"))

        flash("❌ Invalid credentials", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        number = request.form.get("number", "").strip()
        password = generate_password_hash(request.form.get("password", "").strip())

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, number, password) VALUES (?, ?, ?, ?)",
                (name, email, number, password)
            )
            conn.commit()
            conn.close()

            flash("👤 Account created!", "account")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("Email already registered!", "error")
            return redirect(url_for("signup"))

    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return render_template("logout.html")


@app.route("/dashboard")
def dashboard():
    if not session.get("admin_logged_in"):
        flash("⚠️ Admin login required", "error")
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments ORDER BY date DESC, time ASC")
    appointments = cursor.fetchall()
    conn.close()

    return render_template("dashboard.html", appointments=appointments)


@app.route("/dashboard/messages")
def messages():
    if not session.get("admin_logged_in"):
        flash("⛔ Admin access required", "m-error")
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages ORDER BY id DESC")
    all_messages = cursor.fetchall()
    conn.close()

    return render_template("messages.html", messages=all_messages)


@app.route("/dashboard/adddoctor")
def adddoctor():
    if not session.get("admin_logged_in"):
        flash("⛔ Admin access required", "m-error")
        return redirect(url_for("admin_login"))

    return render_template("adddoctor.html")


@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM admins WHERE email = ?", (email,))
        admin = cursor.fetchone()
        conn.close()

        if admin and check_password_hash(admin["password"], password):
            session["admin_logged_in"] = True
            flash("✅ Admin login successful!", "in-success")
            return redirect(url_for("dashboard"))

        flash("❌ Invalid admin credentials", "in-error")
        return redirect(url_for("admin_login"))

    return render_template("admin-login.html")


@app.route("/admin-signup", methods=["GET", "POST"])
def admin_signup():
    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip()
        password = generate_password_hash(request.form.get("password", "").strip())

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO admins (fullname, email, password) VALUES (?, ?, ?)",
                (fullname, email, password)
            )
            conn.commit()
            conn.close()

            flash("✅ Admin account created!", "up-success")
            return redirect(url_for("admin_login"))

        except sqlite3.IntegrityError:
            flash("❌ Admin email already registered!", "up-error")
            return redirect(url_for("admin_signup"))

    return render_template("admin-signup.html")


@app.route("/admin-logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    flash("🔐 Logged out from Admin.", "info")
    return redirect(url_for("admin_login"))


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

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        print("✅ Email sent to", to_email)

    except Exception as e:
        print("❌ Email error:", e)


@app.route("/update_status/<int:id>", methods=["POST"])
def update_status(id):
    if not session.get("admin_logged_in"):
        flash("⚠️ Admin login required", "error")
        return redirect(url_for("admin_login"))

    new_status = request.form.get("status", "").strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE appointments SET status = ? WHERE id = ?",
        (new_status, id)
    )

    cursor.execute("SELECT email FROM appointments WHERE id = ?", (id,))
    row = cursor.fetchone()

    conn.commit()
    conn.close()

    email = row["email"] if row else None

    if email:
        if new_status.lower() == "approved":
            subject = "✅ Appointment Approved - LifeCare Clinic"
            body = "Your appointment has been approved."
            threading.Thread(target=send_email, args=(email, subject, body)).start()

        elif new_status.lower() == "cancelled":
            subject = "❌ Appointment Cancelled - LifeCare Clinic"
            body = "Your appointment has been cancelled."
            threading.Thread(target=send_email, args=(email, subject, body)).start()

    flash("Status updated", "s-updated")
    return redirect(url_for("dashboard"))


@app.route("/delete_appointment/<int:id>", methods=["POST"])
def delete_appointment(id):
    if not session.get("admin_logged_in"):
        flash("⚠️ Admin login required", "error")
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM appointments WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    flash("Appointment deleted", "s-deleted")
    return redirect(url_for("dashboard"))


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
