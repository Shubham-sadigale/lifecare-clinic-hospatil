import threading
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "shubham_secret")

WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "shubham_webhook")

DB_NAME = os.environ.get("DB_NAME", "shubham_hospital.db")


def init_db():
    with sqlite3.connect(DB_NAME, timeout=10) as conn:
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            number TEXT NOT NULL,
            password TEXT NOT NULL
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            number TEXT NOT NULL,
            message TEXT
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS appointments (
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
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )''')

        cursor.execute("SELECT * FROM admins WHERE email=?", ("sadigaleshubham8@gmail.com",))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO admins (fullname,email,password) VALUES (?,?,?)",
                           ("Default Admin","sadigaleshubham8@gmail.com",generate_password_hash("admin123")))

        conn.commit()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/home")
def main():
    return redirect(url_for("home"))


@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT name,password FROM users WHERE email=?", (email,))
        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[1], password):

            session["user"] = user[0]

            flash("✅ Login successful!","success")

            return redirect(url_for("home"))

        else:

            flash("❌ Invalid credentials","error")

            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/signup", methods=["GET","POST"])
def signup():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        number = request.form["number"]
        password = generate_password_hash(request.form["password"])

        try:

            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            cursor.execute("INSERT INTO users (name,email,number,password) VALUES (?,?,?,?)",
                           (name,email,number,password))

            conn.commit()
            conn.close()

            flash("👤 Account created!","account")

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:

            flash("Email already registered!")

            return redirect(url_for("signup"))

    return render_template("signup.html")


@app.route("/logout")
def logout():

    session.pop("user",None)

    return render_template("logout.html")


@app.route("/appointments", methods=["GET","POST"])
def appointments():

    if request.method == "POST":

        data = {

            "firstname": request.form["firstname"],
            "lastname": request.form["lastname"],
            "email": request.form["email"],
            "number": request.form["number"],
            "doctor": request.form["doctor"],
            "date": request.form["date"],
            "time": request.form["time"],
            "appointment_type": request.form["type"],
            "notes": request.form.get("notes",""),
            "status":"Pending"

        }

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO appointments
            (firstname,lastname,email,number,doctor,date,time,appointment_type,notes,status)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        ''',(data["firstname"],data["lastname"],data["email"],data["number"],data["doctor"],
             data["date"],data["time"],data["appointment_type"],data["notes"],data["status"]))

        conn.commit()
        conn.close()

        flash("📅 Appointment request sent!","appointment")

        return redirect(url_for("home"))

    return render_template("appointment.html")


@app.route("/doctors")
def doctors():
    return render_template("doctor.html")


@app.route("/aboutus")
def about_us():
    return render_template("aboutus.html")


@app.route("/contact", methods=["GET","POST"])
def contact():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        number = request.form["number"]
        message = request.form.get("message","")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("INSERT INTO messages (name,email,number,message) VALUES (?,?,?,?)",
                       (name,email,number,message))

        conn.commit()
        conn.close()

        flash("📤 Message successfully sent!","message")

        return redirect(url_for("contact"))

    return render_template("contact.html")


@app.route("/dashboard")
def dashboard():

    if not session.get("admin_logged_in"):

        flash("⚠️ Admin login required","error")

        return redirect(url_for("admin_login"))

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM appointments ORDER BY date DESC")

    appointments = cursor.fetchall()

    conn.close()

    return render_template("dashboard.html",appointments=appointments)


@app.route("/dashboard/messages")
def messages():

    if not session.get("admin_logged_in"):

        flash("⛔ Admin access required","m-error")

        return redirect(url_for("admin_login"))

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM messages ORDER BY id DESC")

    messages = cursor.fetchall()

    conn.close()

    return render_template("messages.html",messages=messages)


@app.route("/dashboard/adddoctor")
def adddoctor():
    return render_template("adddoctor.html")


@app.route("/admin-login", methods=["GET","POST"])
def admin_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT password FROM admins WHERE email=?", (email,))
        admin = cursor.fetchone()

        conn.close()

        if admin and check_password_hash(admin[0],password):

            session["admin_logged_in"] = True

            flash("✅ Admin login successful!","in-success")

            return redirect(url_for("dashboard"))

        else:

            flash("❌ Invalid admin credentials","in-error")

            return redirect(url_for("admin_login"))

    return render_template("admin-login.html")


@app.route("/admin-signup", methods=["GET","POST"])
def admin_signup():

    if request.method == "POST":

        fullname = request.form["fullname"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        try:

            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            cursor.execute("INSERT INTO admins (fullname,email,password) VALUES (?,?,?)",
                           (fullname,email,password))

            conn.commit()
            conn.close()

            flash("✅ Admin account created!","up-success")

            return redirect(url_for("admin_login"))

        except sqlite3.IntegrityError:

            flash("❌ Admin email already registered!","up-error")

            return redirect(url_for("admin_signup"))

    return render_template("admin-signup.html")


@app.route("/admin-logout")
def admin_logout():

    session.pop("admin_logged_in",None)

    flash("🔐 Logged out from Admin.","info")

    return redirect(url_for("admin_login"))


def send_email(to_email, subject, body):

    try:

        sender_email = os.environ.get("SENDER_EMAIL")
        sender_password = os.environ.get("SENDER_PASSWORD")

        msg = MIMEText(body)

        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = to_email

        server = smtplib.SMTP("smtp.gmail.com",587)
        server.starttls()
        server.login(sender_email,sender_password)
        server.send_message(msg)
        server.quit()

    except Exception as e:

        print("Email error:",e)


@app.route("/update_status/<int:id>", methods=["POST"])
def update_status(id):

    new_status = request.form.get("status")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("UPDATE appointments SET status=? WHERE id=?", (new_status,id))

    cursor.execute("SELECT email FROM appointments WHERE id=?", (id,))
    row = cursor.fetchone()

    conn.commit()
    conn.close()

    email = row[0] if row else None

    if email:

        if new_status.lower()=="approved":

            subject="Appointment Approved"
            body="Your appointment has been approved."

            threading.Thread(target=send_email,args=(email,subject,body)).start()

        elif new_status.lower()=="cancelled":

            subject="Appointment Cancelled"
            body="Your appointment has been cancelled."

            threading.Thread(target=send_email,args=(email,subject,body)).start()

    flash("Status updated","s-updated")

    return redirect(url_for("dashboard"))


@app.route("/delete_appointment/<int:id>", methods=["POST"])
def delete_appointment(id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM appointments WHERE id=?", (id,))

    conn.commit()
    conn.close()

    flash("Appointment deleted","s-deleted")

    return redirect(url_for("dashboard"))


if __name__ == "__main__":

    init_db()

    app.run(host="0.0.0.0",port=10000)