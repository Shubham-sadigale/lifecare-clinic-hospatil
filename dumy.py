# from flask import Flask, flash, render_template, request, redirect, url_for, session
# from datetime import timedelta

# app = Flask(__name__)
# app.secret_key= "data"
# app.permanent_session_lifetime = timedelta(hours=5)

# @app.route("/")
# def home():
#     return render_template('index.html')

# # Login Route
# @app.route('/login', methods=["POST","GET"])
# def login():
#     if request.method == "POST":
#         session.permanent = True
        
#         return redirect(url_for("home"))
#     else:
        
#         return redirect(url_for("home"))
    
#     return render_template('login.html')


# @app.route('/logout')
# def logout():
#     session.pop("user", None)
#     flash("You have been Logged Out !")
#     return redirect(url_for("login"))

# # Signup Route
# @app.route('/signup')
# def signup():
#     return render_template('signup.html')

# @app.route("/admin")
# def admin():
#     return redirect(url_for('home'))

# @app.route("/admin-login")
# def admin_login():
#     return render_template('admin-login.html')

# @app.route("/admin-signup")
# def admin_signup():
#     return render_template('admin-signup.html')


# @app.route("/appointments")
# def appointments():
#     return render_template('appointment.html')

# @app.route("/doctors")
# def doctors():
#     return render_template('doctor.html')

# @app.route("/aboutus")
# def about_us():
#     return render_template('aboutus.html')


# # Step 5: Run Server and Create DB
# if __name__ == "__main__":
   
#     app.run(debug=True, port=4518)





























# from flask import Flask, render_template, request, redirect, url_for
# from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime



# app = Flask(__name__)

# # Step 1: Database Configuration
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# # Step 2: Initialize SQLAlchemy
# db = SQLAlchemy(app)

# # Step 4: Define Routes
# @app.route("/")
# def hello_world():
#     return render_template('index.html')

# @app.route("/appointments")
# def appointments():
#     return render_template('appointment.html')

# @app.route("/doctors")
# def doctors():
#     return render_template('doctor.html')

# @app.route("/aboutus")
# def about_us():
#     return render_template('aboutus.html')

# # Login Route
# @app.route('/login')
# def login():
#     return render_template('patient.html')

# # Signup Route
# @app.route('/signup')
# def signup():
#     return render_template('patient-register.html')


# @app.route("/admin-login")
# def admin_login():
#     return render_template('admin.html')

# @app.route("/admin-signup")
# def admin_signup():
#     return render_template('admin-register.html')

# # Step 5: Run Server and Create DB
# if __name__ == "__main__":
   
#     app.run(debug=True, port=6969)























# # 🧙‍♂️ Magic Hospital Server Code (app.py)
# from flask import Flask, render_template, request, redirect, url_for
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import UserMixin, LoginManager, login_user, logout_user

# app = Flask(__name__)
# app.secret_key = 'super-secret-key-123'  # 🔑 Our magic spell protector

# # 🧚 Setup Fairy Database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
# db = SQLAlchemy(app)

# # 👨⚕️ Doctor Table (Like a LEGO structure)
# class Doctor(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(80))
#     special = db.Column(db.String(50))

# # 👧 User Table (For patients and admins)
# class User(UserMixin, db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True)
#     password = db.Column(db.String(80))
#     is_admin = db.Column(db.Boolean, default=False)

# # 🧙 Login Magic Setup
# login_manager = LoginManager()
# login_manager.init_app(app)

# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))

# # 🌈 Our Colorful Website Pages
# @app.route('/')
# def home():
#     return render_template('home.html')

# @app.route('/about')
# def about():
#     return render_template('about.html')

# @app.route('/doctors')
# def doctors():
#     all_doctors = Doctor.query.all()
#     return render_template('doctors.html', doctors=all_doctors)

# # 📅 Appointment Page
# @app.route('/appointments', methods=['GET', 'POST'])
# def appointments():
#     if request.method == 'POST':
#         # 🎯 We'll add appointment saving code here later
#         return redirect(url_for('home'))
#     return render_template('appointments.html')

# # 🔒 Login/Register Pages
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         user = User.query.filter_by(username=username).first()
#         if user and user.password == password:
#             login_user(user)
#             return redirect(url_for('home'))
#     return render_template('login.html')

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         new_user = User(username=username, password=password)
#         db.session.add(new_user)
#         db.session.commit()
#         return redirect(url_for('login'))
#     return render_template('register.html')

# # 🚪 Logout Route
# @app.route('/logout')
# def logout():
#     logout_user()
#     return redirect(url_for('home'))

# # 🏥 Let's Build Our Hospital!
# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()  # ✨ Create database if it doesn't exist
#         # Add some sample doctors
#         if not Doctor.query.first():
#             doctors = [
#                 Doctor(name="Dr. Teddy Bear", special="Hug Therapy"),
#                 Doctor(name="Dr. Bunny", special="Carrot Nutrition"),
#                 Doctor(name="Dr. Owl", special="Nighttime Stories")
#             ]
#             db.session.add_all(doctors)
#             db.session.commit()
#     app.run(debug=True)  # 🚀 Launch our rocket server!

























# Create all necessary tables
# def init_db():
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
    
#     # Users table
#     cursor.execute('''CREATE TABLE IF NOT EXISTS users (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         name TEXT NOT NULL,
#         email TEXT UNIQUE NOT NULL,
#         password TEXT NOT NULL
#     )''')

#     # Appointments table
#     # cursor.execute('''CREATE TABLE IF NOT EXISTS appointments (
#     #     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     #     firstname TEXT NOT NULL,
#     #     lastname TEXT NOT NULL,
#     #     email TEXT NOT NULL,
#     #     number TEXT NOT NULL,
#     #     doctor TEXT NOT NULL,
#     #     date TEXT NOT NULL,
#     #     time TEXT NOT NULL,
#     #     appointment_type TEXT NOT NULL,
#     #     notes TEXT
#     # )''')
    
#     # Admin table
#     cursor.execute('''CREATE TABLE IF NOT EXISTS admins (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         fullname TEXT NOT NULL,
#         email TEXT UNIQUE NOT NULL,
#         password TEXT NOT NULL
#     )''')
    
#     # Insert default admin if none exists
#     cursor.execute("SELECT * FROM admins")
#     if cursor.fetchone() is None:
#         cursor.execute("INSERT INTO admins (email, password) VALUES (?, ?)", (
#             "admin@example.com", generate_password_hash("admin123")
#         ))
        
#     # Create tables if not exist
#     cursor.execute('''CREATE TABLE IF NOT EXISTS users (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         name TEXT NOT NULL,
#         email TEXT UNIQUE NOT NULL,
#         password TEXT NOT NULL
#     )''')

#     cursor.execute('''CREATE TABLE IF NOT EXISTS appointments (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         firstname TEXT NOT NULL,
#         lastname TEXT NOT NULL,
#         email TEXT NOT NULL,
#         number TEXT NOT NULL,
#         doctor TEXT NOT NULL,
#         date TEXT NOT NULL,
#         time TEXT NOT NULL,
#         appointment_type TEXT NOT NULL,
#         notes TEXT
#     )''')

#     cursor.execute('''CREATE TABLE IF NOT EXISTS admins (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         fullname TEXT NOT NULL,
#         email TEXT UNIQUE NOT NULL,
#         password TEXT NOT NULL
#     )''')

#     # Check if 'status' column already exists
#     cursor.execute("PRAGMA table_info(appointments)")
#     columns = [col[1] for col in cursor.fetchall()]
#     if 'status' not in columns:
#         cursor.execute("ALTER TABLE appointments ADD COLUMN status TEXT DEFAULT 'Pending'")
        
#     # Add 'fullname' column to admins if not exists
#     cursor.execute("PRAGMA table_info(admins)")
#     admin_columns = [col[1] for col in cursor.fetchall()]
#     if 'fullname' not in admin_columns:
#         cursor.execute("ALTER TABLE admins ADD COLUMN fullname TEXT")    

#     conn.commit()
#     conn.close()











# @app.route("/update_status/<int:id>", methods=["POST"])
# def update_status(id):
#     new_status = request.form["status"]

#     # Update the status in the database
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
#     cursor.execute("UPDATE appointments SET status=? WHERE id=?", (new_status, id))

#     # Get the user's email address
#     cursor.execute("SELECT email FROM appointments WHERE id=?", (id,))
#     email = cursor.fetchone()[0]
#     conn.commit()
#     conn.close()

#     # Send email for Approved or Cancelled
#     if new_status == "Cancelled":
#         subject = f"Your Appointment has been {new_status}"
#         body = f"""Dear Patient,

# Your appointment has been {new_status.lower()}.

# Regards,  
# Orchid Clinic"""
#         send_email(email, subject, body)
        
#     if new_status == "Approved":
#     payment_link = create_payment_link(500, email)  # Change 500 to your actual fee
#     subject = "Your Appointment is Approved – Payment Required"
#     body = f"""Dear Patient,

# Your appointment has been approved. Please complete the payment of ₹500 at the link below:

# {payment_link}

# Regards,
# Orchid Clinic
# """
#     send_email(email, subject, body)    

#     flash(f"📧 Appointment status updated to {new_status}", "s-updated")
#     return redirect(url_for("dashboard"))
