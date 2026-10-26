from ..extensions import db

class Singles(db.Model):
    __tablename__ = 'singles'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(64), nullable=False)
    artist_name = db.Column(db.String(64), nullable=False)
    album = db.Column(db.String(64), nullable=False)
    links = db.Column(db.Text, nullable=False)
    buy_link = db.Column(db.Text, nullable=True)


class Albums(db.Model):
    __tablename__ = 'albums'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    artist_name = db.Column(db.String(128), nullable=False)
    released_date = db.Column(db.Date, nullable=False)
    link = db.Column(db.Text, nullable=False)
    buy_link = db.Column(db.Text, nullable=True)