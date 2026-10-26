from ..extensions import db
from flask_login import UserMixin
from werkzeug.security import check_password_hash

class Admin(db.Model, UserMixin):
    __tablename__ = "admin"

    uid = db.Column(db.Integer, primary_key=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    totp_secret = db.Column(db.String(32), nullable=True)
    totp_enabled = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"{self.email}"
    
    def get_id(self):
        return str(self.uid)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
