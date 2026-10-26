from ..extensions import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = "user"

    uid = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    short_about = db.Column(db.Text, nullable=False)

    def get_id(self):
        return str(self.uid)
