
from ..extensions import db


class AlbumTrack(db.Model):
    __tablename__ = "album_tracks"

    id = db.Column(db.Integer, primary_key=True)

    album_id = db.Column(
        db.Integer,
        db.ForeignKey("albums.id"),
        nullable=False,
        index=True,
    )

    track_number = db.Column(db.Integer, nullable=False)
    track_name = db.Column(db.String(200), nullable=False)
    duration = db.Column(db.String(10), nullable=True)

    album = db.relationship(
        "Album",
        back_populates="tracklist",
    )

    __table_args__ = (
        db.UniqueConstraint(
            "album_id",
            "track_number",
            name="uq_album_track_number",
        ),
        db.CheckConstraint(
            "track_number > 0",
            name="ck_album_track_number_positive",
        ),
    )

    def __repr__(self):
        return f"<AlbumTrack {self.track_number}: {self.track_name!r}>"
