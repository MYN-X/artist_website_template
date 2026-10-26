from ..extensions import db


class LinktreeLink(db.Model):
    __tablename__ = 'linktree_link'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    text = db.Column(db.Text, nullable=False)  # Button text with emoji
    url = db.Column(db.Text, nullable=False)
    is_secondary = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, nullable=False, default=0)

class LinktreeConfig(db.Model):
    __tablename__ = 'linktree_config'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    avatar = db.Column(db.Text, nullable=False, default='O')
    name = db.Column(db.Text, nullable=False, default='OOM DASS')
    handle = db.Column(db.Text, nullable=False, default='')
    bio = db.Column(db.Text, nullable=False, default='')
    email = db.Column(db.Text, nullable=False, default='example@gmail.com')