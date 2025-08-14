from ..models import User
from app import db

def register_user(data):
    user = User(username=data['username'], password=data['password'])
    db.session.add(user)
    db.session.commit()
    return user

def login_user(data):
    user = User.query.filter_by(username=data['username']).first()
    return user if user and user.check_password(data['password']) else None