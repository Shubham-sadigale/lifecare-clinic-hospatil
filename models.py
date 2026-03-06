# from app import db
















# from app import db

# class Patient_Login(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100))
#     email = db.Column(db.String(50), unique=True)
#     password = db.Column(db.String(20))
    
# class Patient_Signup(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100))
#     email = db.Column(db.String(100), unique=True)
#     password = db.Column(db.String(100))    
#     c-password = db.Column(db.String(100))    
    
# class Admin_Login(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100))
#     email = db.Column(db.String(100), unique=True)
#     password = db.Column(db.String(100))
    
# class Admin_Signup(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100))
#     email = db.Column(db.String(100), unique=True)
#     password = db.Column(db.String(100))    
#     cpassword = db.Column(db.String(100))    
    

# from app import db

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = name = db.Column(db.String(100))
#     email = db.Column(db.String(100), unique=True)
#     password = db.Column(db.String(100))

# class Admin(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(100), unique=True)
#     password = db.Column(db.String(100))

# class Appointment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer)
#     doctor_name = db.Column(db.String(100))
#     date = db.Column(db.String(100))
#     time = db.Column(db.String(100))
