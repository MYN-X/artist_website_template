from ..extensions import db

class Message(db.Model):
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    message = db.Column(db.Text, nullable=False)
    nda_requested = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime, nullable=False, default=db.func.now())
    read = db.Column(db.Boolean, default=False)