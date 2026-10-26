from ..extensions import db

class Blog(db.Model):
    __tablename__ = 'blog'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=db.func.now())
    reading_time = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"<Blog {self.title} (artist_id={self.artist_id})>"