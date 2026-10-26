from ..extensions import db

# This model will be deprecated soon, as services will no longer be a part of the portfolio. The services will be moved to a separate platform or service.

class Service(db.Model):
    __tablename__ = 'service'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.Text, nullable=True)
    price_monthly = db.Column(db.Float, nullable=True)
    price_yearly = db.Column(db.Float, nullable=True)

