from werkzeug.security import check_password_hash
from app.models.user import User
from app.extensions import db

class AuthService:
    @staticmethod
    def authenticate(username, password):
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            return user
        return None

    @staticmethod
    def change_password(user_id, old_password, new_password):
        user = User.query.get(user_id)
        if user and check_password_hash(user.password_hash, old_password):
            user.set_password(new_password)
            db.session.commit()
            return True
        return False