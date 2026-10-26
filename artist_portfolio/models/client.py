from ..extensions import db

class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)

    ga4_measurement_id = db.Column(db.String(20), nullable=True)