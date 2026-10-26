import os
from sqlalchemy import inspect
from werkzeug.security import generate_password_hash
import json


def _table_exists(db, table_name: str) -> bool:
    try:
        inspector = inspect(db.engine)
        return table_name in inspector.get_table_names()
    except Exception:
        return False


def seed_all(db):
    if not _table_exists(db, "admin"):
        return

    seed_media_config(db)
    seed_user_profile(db)
    seed_foundation_about(db)
    seed_journey_defaults(db)
    db.session.commit()


def create_admin(db, email: str, password: str):
    # from .models import Admin
    from .models import Admin

    email = email.strip()
    if not email:
        raise ValueError("Admin email is required.")
    if len(password) < 16:
        raise ValueError("Admin password must be at least 16 characters long.")
    if Admin.query.first():
        raise ValueError("An admin account already exists.")

    try:
        db.session.add(Admin(
            email=email,
            password=generate_password_hash(password),
            totp_enabled=False,
        ))
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def seed_user_profile(db):
    from .models import User

    if User.query.first():
        return

    db.session.add(User(
        name=os.getenv("INIT_PROFILE_NAME", "Artist Name"),
        short_about=os.getenv("INIT_PROFILE_SHORT_ABOUT", "Edit this in the CMS.")
    ))


def seed_foundation_about(db):
    from .models import FoundationAbout

    defaults = [
        {"id": 1, "title": "paragraph_one", "paragraphs": "Edit this in the CMS."},
        {"id": 2, "title": "paragraph_two", "paragraphs": "Edit this in the CMS."},
    ]

    for row in defaults:
        if not FoundationAbout.query.get(row["id"]):
            db.session.add(FoundationAbout(**row))


def seed_journey_defaults(db):
    from .models import Journey

    defaults = [
        {"year": 2015, "desc": "Started writing and performing original material."},
        {"year": 2018, "desc": "Released early demos and refined artistic direction."},
    ]

    for row in defaults:
        if not Journey.query.filter_by(year=row["year"]).first():
            db.session.add(Journey(**row))




def seed_media_config(db):
    from .models import MediaConfig

    defaults = {
        "latest": [
            "https://youtube.com",
            "https://bandlab"
        ],
        "eps": [
            {
                "title": "Solitude",
                "year": "2023",
                "stream_url": "https://youtube.com/@oom_dass",
                "buy_url": "https://bandcamp.com",
                "artist": None
            }
        ],
        "featured_playlist": "https://open.spotify.com/@oom_dass",
        "streaming": {
            "spotify": "https://spotify.com",
            "soundcloud": "https://on.soundcloud.com/vytY8liCK5auv86bYK",
            "youtubemusic": "https://www.youtube.com/@ConnorOdyssey",
            "applemusic": "https://applemusic.com/@oom_dass",
            "audiomack": "https://audiomack.com/@oom_dass",
            "bandcamp": "https://amazon.com"
        }
    }

    for key, value in defaults.items():
        exists = MediaConfig.query.filter_by(key=key).first()
        if exists:
            continue

        # Store JSON as string when needed
        if isinstance(value, (dict, list)):
            stored_value = json.dumps(value)
        else:
            stored_value = value

        db.session.add(
            MediaConfig(
                key=key,
                value=stored_value
            )
        )