import qrcode
import base64
from io import BytesIO
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from ..database.login import AdminLogin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user
from ..models import Admin, User, Skills, Blog, ProfileImg, Service, FAQ, Message, Gallery, AboutSection, MediaConfig, Event, LinktreeLink, LinktreeConfig, Singles, Albums, Expertise, HeroAbout, Testimonials, FoundationAbout, Journey, Client
from werkzeug.utils import secure_filename
import cloudinary.uploader
import os
from datetime import datetime
import logging
admin_details = AdminLogin()
import pyotp
import json, os
from pathlib import Path
logging.basicConfig(level=logging.DEBUG)
from .config import init_cloudinary
from ..upload_validation import validate_image_upload

init_cloudinary()

admin = Blueprint(
    "admin",
    __name__,
    template_folder="html",
    static_folder="scripts",
    static_url_path="/admin/static" 
)


@admin.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get('email')
    password = request.form.get('password')

    print(email)
    print(password)
    admin_user = Admin.query.filter_by(email=email).first()
    print(admin_user)

    if not admin_user:
       
        flash('Invalid credentials', 'error')
        return redirect(url_for('admin.admin_login'))

    if not check_password_hash(admin_user.password, password):
        flash('Invalid credentials', 'error')
        return redirect(url_for('admin.admin_login'))

    print(f"What is totp: {admin_user.totp_enabled}")
    
    if admin_user.totp_enabled:
        session['pending_admin_id'] = admin_user.uid
        return redirect(url_for('admin.verify_totp'))

    print("You're logged in...")
    login_user(admin_user)
    return redirect(url_for('admin_home.admin_dashboard'))

@admin.route('/login/totp', methods=['GET', 'POST'])
def verify_totp():
    if request.method == "GET":
        return render_template("enter_totp.html")

    code = request.form.get('code')

    pending_id = session.get('pending_admin_id')
    if not pending_id:
        flash("Session expired. Try logging in again.", "error")
        return redirect(url_for('admin.admin_login'))

    admin_user = Admin.query.get(pending_id)

    totp = pyotp.TOTP(admin_user.totp_secret)

    if totp.verify(code, valid_window=1):
        # Success
        login_user(admin_user)
        session.pop('pending_admin_id')
        return redirect(url_for('admin_home.admin_dashboard'))
    else:
        flash("Invalid or expired code", "error")
        return redirect(url_for('admin.verify_totp'))

@admin.route('/totp/setup')
def totp_setup():
    admin_user = Admin.query.first()  
    # If already enabled, skip
    if admin_user.totp_enabled:
        flash("TOTP already enabled.", "info")
        return redirect(url_for('admin.admin_dashboard'))

    secret = pyotp.random_base32()
    session['pending_totp_secret'] = secret

    totp = pyotp.TOTP(secret)

    uri = totp.provisioning_uri(
        name=admin_user.email,
        issuer_name="MyPortfolioCMS"
    )

    # Create QR code
    img = qrcode.make(uri)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render_template("totp_setup.html", qr=qr_base64, secret=secret)

@admin.route('/totp/confirm', methods=['POST'])
def totp_confirm():
    code = request.form.get('code')
    secret = session.get('pending_totp_secret')

    from ..app import db

    if not secret:
        flash("Setup session expired. Try again.", "error")
        return redirect(url_for('admin.totp_setup'))

    totp = pyotp.TOTP(secret)

    if totp.verify(code):
        admin_user = Admin.query.first()
        admin_user.totp_secret = secret
        admin_user.totp_enabled = True
        db.session.commit()

        session.pop('pending_totp_secret')

        flash("TOTP enabled successfully!", "success")
        return redirect(url_for('admin.admin_dashboard'))

    flash("Invalid code. Try again.", "error")
    return redirect(url_for('admin.totp_setup'))


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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

#==============================================================Linktree===================================================
#======================================================================================================================
@admin.route('/manage linktree')
@login_required
def manage_linktree():
    from ..app import db
    
   
    links = LinktreeLink.query.order_by(LinktreeLink.order).all()
    config = LinktreeConfig.query.first()
    
    if not config:
        config = LinktreeConfig()
        db.session.add(config)
        db.session.commit()
    
    return render_template("manage_linktree.html", links=links, config=config)

@admin.route('/update/linktree/config', methods=['POST'])
@login_required
def update_linktree_config():
    from app import db
    data = request.get_json()

    config = LinktreeConfig.query.first()
    if not config:
       
        config = LinktreeConfig()
        db.session.add(config)
    
    if data.get('avatar'):
        config.avatar = data.get('avatar')
    if data.get('name'):
        config.name = data.get('name')
    if data.get('handle'):
        config.handle = data.get('handle')
    if data.get('bio'):
        config.bio = data.get('bio')
    if data.get('email'):
        config.email = data.get('email')
    
    db.session.commit()
    return {"message": "Configuration updated"}, 200


@admin.route('/create/linktree/link', methods=['POST'])
@login_required
def create_linktree_link():
    from ..app import db
    # from flask import g
    data = request.get_json()
    text = data.get('text')
    url = data.get('url')
    is_secondary = data.get('is_secondary', False)
    
    if not text or not url:
        return {"message": "Text and URL are required"}, 400
    
    # Get the next order value for current artist
    max_order = db.session.query(db.func.max(LinktreeLink.order)).scalar() or 0
    
    new_link = LinktreeLink(
        text=text,
        url=url,
        is_secondary=is_secondary,
        order=max_order + 1
    )
    db.session.add(new_link)
    db.session.commit()
    return {"message": "Link created successfully"}, 201

@admin.route('/edit/linktree/link/<int:link_id>', methods=['POST'])
@login_required
def edit_linktree_link(link_id):
    from ..app import db
    # from flask import g
    link = LinktreeLink.query.filter_by(
        id=link_id
    ).first_or_404()
    data = request.get_json()
    
    link.text = data.get('text', link.text)
    link.url = data.get('url', link.url)
    link.is_secondary = data.get('is_secondary', link.is_secondary)
    
    db.session.commit()
    return {"message": "Link updated successfully"}, 200

@admin.route('/delete/linktree/link/<int:link_id>', methods=['POST'])
@login_required
def delete_linktree_link(link_id):
    from ..app import db
    # from flask import g
    link = LinktreeLink.query.filter_by(
        id=link_id
    ).first_or_404()
    db.session.delete(link)
    db.session.commit()
    return {"message": "Link deleted successfully"}, 200