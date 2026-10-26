from ..extensions import db

class FAQ(db.Model):
    __tablename__ = 'faq'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)