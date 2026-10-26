from datetime import datetime
import json
import os
from pathlib import Path
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user
import logging

from ..models import (
    Admin, User, Skills, 
    Blog, ProfileImg, Service, 
    FAQ, Message, Gallery, 
    AboutSection, MediaConfig, 
    Event, LinktreeLink, 
    LinktreeConfig, Singles, 
    Albums, Expertise, HeroAbout, 
    Testimonials, FoundationAbout, 
    Journey, Client, Album, AlbumTrack, AlbumStreamingLink
    )
logging.basicConfig(level=logging.DEBUG)


admin_media = Blueprint(
    "admin_media",
    __name__,
    template_folder="html",
    static_folder="scripts",
    static_url_path="/admin/static"
)


def _save_media_to_db(media_dict):
    from ..app import db
    import json
    try:
        for k, v in media_dict.items():
            entry = MediaConfig.query.filter_by(key=k).first()
            if isinstance(v, (dict, list)):
                value = json.dumps(v, ensure_ascii=False)
            else:
                value = str(v) if v is not None else ''
            if entry:
                entry.value = value
            else:
                entry = MediaConfig(key=k, value=value)
                db.session.add(entry)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False

def _get_media_from_db():
    from ..app import db
    import json
    media = {}
    try:
        entries = MediaConfig.query.all()
        for e in entries:
            if e.key in ('streaming', 'eps', 'latest'):
                try:
                    media[e.key] = json.loads(e.value) if e.value else {}
                except Exception:
                    media[e.key] = {}
            else:
                media[e.key] = e.value or ''
    except Exception:
        media = {}
    return media


@admin_media.route('/manage/media')
@login_required
def manage_media():
   
    from ..app import db

    config = LinktreeConfig.query.first()
    handle = config.handle if config else ''
    
    media = {}
    # Try DB first
    try:
        entries = MediaConfig.query.all()
        if entries:
            for e in entries:
                if e.key in ('streaming', 'eps', 'latest'):
                    try:
                        media[e.key] = json.loads(e.value) if e.value else {}
                    except Exception:
                        media[e.key] = {}
                else:
                    media[e.key] = e.value or ''
        else:
            # fallback to file.json
            base = os.path.join(os.path.dirname(__file__), '..')
            cfg_path = os.path.join(base, 'file.json')
            try:
                with open(cfg_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    media = data.get('media', {})
            except Exception:
                media = {}
    except Exception:
        media = {}

        # TODO: update which album model is used

    # album = db.session.get(Album, 1)
    # all_albums = Album.query.all()
    all_albums = Album.query.all()

    # if album:
    #     print(album.album_name)

    # for track in album.tracklist:
    #     print(track.track_number, track.track_name, track.duration)

    # for link in album.streaming_links:
    #     print(link.platform, link.url)

    singles = Singles.query.all()
    albums = Albums.query.all()

    streaming = media.get('streaming', {})
    featured_playlist = media.get('featured_playlist', '')
    eps = media.get('eps', [])
    latest = media.get('latest', [])
    return render_template('manage_media.html', streaming=streaming, 
                           featured_playlist=featured_playlist, eps=eps, 
                           latest=latest, singles=singles, 
                           albums=albums, handle=handle,
                           all_albums=all_albums,
                           )


@admin_media.route('/update/streaming/links', methods=['POST'])
@login_required
def update_streaming_links():
    data = request.get_json() or {}
    streaming = data.get('streaming', {})
    # Save to DB
    media = _get_media_from_db()
    media['streaming'] = streaming
    ok = _save_media_to_db({'streaming': streaming})
    if ok:
        return {"message": "Streaming links updated"}, 200
    return {"message": "Error saving streaming links"}, 500

@admin_media.route('/update/featured/playlist', methods=['POST'])
@login_required
def update_featured_playlist():
    data = request.get_json() or {}
    playlist = data.get('playlist', '')
    ok = _save_media_to_db({'featured_playlist': playlist})
    if ok:
        return {"message": "Featured playlist updated"}, 200
    return {"message": "Error saving playlist"}, 500


@admin_media.route('/add/album', methods=['POST'])
def add_or_update_album():
    
    from ..app import db
    data = request.get_json()

    try:
        released_date = datetime.strptime(
            data.get('released_date'), "%Y-%m-%d"
        ).date()
    except Exception:
        return jsonify({'message': 'Invalid release date'}), 400

    title = data.get('title')
    artist = data.get('artist')
    link = data.get('link')
    buy_link = data.get('buy_link')


    if not all([title, artist, released_date, link]):
        return jsonify({'message': 'Missing fields'}), 400

    album = Albums.query.filter_by(
        title=title,
        artist_name=artist,
        released_date=released_date
    ).first()

    if album:
        #UPDATE
        album.link = link
        album.buy_link = buy_link
        db.session.commit()
        return jsonify({'message': 'Album updated'}), 200

    #CREATE
    album = Albums(
        title=title,
        artist_name=artist,
        released_date=released_date,
        link=link,
        buy_link=buy_link
    )

    db.session.add(album)
    db.session.commit()

    return jsonify({'message': 'Album created'}), 201

@admin_media.route('/delete/album', methods=['POST'])
def delete_album():
    from ..app import db

    data = request.get_json()

    try:
        released_date = datetime.strptime(
            data.get('released_date'), "%Y-%m-%d"
        ).date()
    except Exception:
        return jsonify({'message': 'Invalid release date'}), 400

    title = data.get('title')
    artist = data.get('artist')

    if not all([title, artist, released_date]):
        return jsonify({'message': 'Missing fields'}), 400

    album = Albums.query.filter_by(
        title=title,
        artist=artist,
        released_date=released_date
    ).first()

    if not album:
        return jsonify({'message': 'Album not found'}), 404

    db.session.delete(album)
    db.session.commit()

    return jsonify({'message': 'Album deleted'}), 200

@admin_media.route('/delete/single', methods=['POST'])
def delete_single():
    from ..app import db
    data = request.get_json()

    title = data.get('title')
    artist = data.get('artist')
    album = data.get('album')

    if not all([title, artist, album]):
        return jsonify({'message': 'Missing fields'}), 400

    single = Singles.query.filter_by(
        title=title,
        artist=artist,
        album=album
    ).first()

    if not single:
        return jsonify({'message': 'Single not found'}), 404

    db.session.delete(single)
    db.session.commit()

    return jsonify({'message': 'Single deleted'}), 200


@admin_media.route('/add/single', methods=['POST'])
def add_single():
    from ..app import db

    data = request.get_json()

    title = data.get('title')
    artist = data.get('artist')
    album = data.get('album')
    links = data.get('links')
    buy_link = data.get('buy_link')

    if not all([title, artist, album, links]):
        return jsonify({'message': 'Missing fields'}), 400

    #Check if single already exists
    single = Singles.query.filter_by(
        title=title,
        artist_name=artist,
        album=album
    ).first()

    if single:
        #UPDATE
        single.links = links
        single.buy_link = buy_link
        db.session.commit()
        return jsonify({'message': 'Single updated'}), 200

    #CREATE
    new_single = Singles(
        title=title,
        artist_name=artist,
        album=album,
        links=links
    )

    db.session.add(new_single)
    db.session.commit()

    return jsonify({'message': 'Single added'}), 201


@admin_media.route('/add/latest', methods=['POST'])
@login_required
def add_latest():
    data = request.get_json() or {}
    new_latest = data.get('latest')
    print(new_latest)
    if not isinstance(new_latest, list):
        return {"message": "Invalid payload"}, 400
    media = _get_media_from_db()
    latest = media.get('latest', {})
    if not isinstance(latest, dict):
        latest = {}
    
    latest['latest'] = new_latest
    print(latest)
    ok = _save_media_to_db(latest)
    ok = True
    if ok:
        return {"message": "Latest single URLs saved"}, 201
    return {"message": "Error saving latest"}, 500

@admin_media.route("/update/handle", methods=["POST"])
@login_required
def update_handle():
    from ..app import db
    data = request.get_json() or {}
    handle = (data.get("handle") or "").strip()
    if not handle:
        return {"message": "Error - Please provide a handle"}, 400 
    print(handle)
    config = LinktreeConfig.query.first()
    if not config:  
        config = LinktreeConfig(handle=handle)
        db.session.add(config)  
    else:
        config.handle = handle  
    db.session.commit()
    return {"message": "Handle updated", "handle": config.handle}, 200

#TODO: Find where this route is used
@admin_media.route('/add eps', methods=['POST'])
@login_required
def add_eps():
    data = request.get_json() or {}
    new_eps = data.get('eps')
    if not isinstance(new_eps, list):
        return {"message": "Invalid payload"}, 400
    media = _get_media_from_db()
    eps = media.get('eps', [])
    if not isinstance(eps, list):
        eps = []
    eps.extend(new_eps)
    ok = _save_media_to_db({'eps': eps})
    if ok:
        return {"message": "EP(s) added"}, 201
    return {"message": "Error saving EPs"}, 500


@admin_media.route('/update/eps', methods=['POST'])
@login_required
def update_eps():
    data = request.get_json() or {}
    eps = data.get('eps')
    if not isinstance(eps, list):
        return {"message": "Invalid payload"}, 400
    ok = _save_media_to_db({'eps': eps})
    if ok:
        return {"message": "EP list updated"}, 200
    return {"message": "Error saving EPs"}, 500


@admin_media.route('/delete/eps/<int:idx>', methods=['DELETE'])
@login_required
def delete_eps(idx):
    media = _get_media_from_db()
    eps = media.get('eps', [])
    if not isinstance(eps, list):
        return {"message": "Index out of range"}, 400
    if 0 <= idx < len(eps):
        eps.pop(idx)
        ok = _save_media_to_db({'eps': eps})
        if ok:
            return {"message": "EP deleted"}, 200
        return {"message": "Error deleting EP"}, 500
    return {"message": "Index out of range"}, 400



