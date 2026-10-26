
from ..extensions import db


class AlbumStreamingLink(db.Model):
    __tablename__ = "album_streaming_links"

    id = db.Column(db.Integer, primary_key=True)

    album_id = db.Column(
        db.Integer,
        db.ForeignKey("albums.id"),
        nullable=False,
        index=True,
    )

    platform = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(1000), nullable=False)

    album = db.relationship(
        "Album",
        back_populates="streaming_links",
    )

    __table_args__ = (
        db.UniqueConstraint(
            "album_id",
            "platform",
            name="uq_album_streaming_platform",
        ),
    )

    def __repr__(self):
        return f"<AlbumStreamingLink {self.platform!r}>"