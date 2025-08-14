from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))
    role = db.Column(db.String(20))  # 'student' or 'teacher'

class Experiment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    algorithm = db.Column(db.String(50))
    parameters = db.Column(db.JSON)
    result = db.Column(db.JSON)
    report = db.Column(db.Text)