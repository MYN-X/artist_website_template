from ..extensions import db

class Event(db.Model):
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=True)
    location = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())