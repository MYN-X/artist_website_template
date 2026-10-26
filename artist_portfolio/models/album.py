
from datetime import date

from ..extensions import db


class Album(db.Model):
    __tablename__ = "albums"

    id = db.Column(db.Integer, primary_key=True)

    album_name = db.Column(db.String(200), nullable=False)
    artist_name = db.Column(db.String(200), nullable=False)

    release_date = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text, nullable=True)
    cover_image_url = db.Column(db.String(500), nullable=True)

    # Relationships
    tracklist = db.relationship(
        "AlbumTrack",
        back_populates="album",
        cascade="all, delete-orphan",
        order_by="AlbumTrack.track_number",
        lazy=True,
    )

    streaming_links = db.relationship(
        "AlbumStreamingLink",
        back_populates="album",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def __repr__(self):
        return f"<Album {self.album_name!r}>"
