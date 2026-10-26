from ..extensions import db

class Gallery(db.Model):
    __tablename__ = 'gallery'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    type = db.Column(db.String(10), nullable=False)
    url = db.Column(db.Text, nullable=False)        # public_id
    cloud_url = db.Column(db.Text, nullable=False)  # actual URL
    title = db.Column(db.Text, nullable=True)
