from ..extensions import db 
from flask_login import UserMixin

class Skills(db.Model, UserMixin):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    skill = db.Column(db.Text, nullable=False)