from ..extensions import db
from flask_login import UserMixin

class ProfileImg(db.Model, UserMixin):
    __tablename__ = 'ProfileImg'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    profile_picture = db.Column(db.Text, nullable=True)
    profile_picture_url = db.Column(db.Text, nullable=True)
    banner_img = db.Column(db.Text, nullable=True)
    banner_picture_url = db.Column(db.Text, nullable=True)