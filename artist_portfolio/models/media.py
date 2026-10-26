from ..extensions import db

class MediaConfig(db.Model):
    __tablename__ = 'media_config'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    key = db.Column(db.String(64), nullable=False, unique=True)
    value = db.Column(db.Text, nullable=True)  # JSON string or plain text