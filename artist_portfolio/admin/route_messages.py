from pathlib import Path
from ..models import Admin, User, Skills, Blog, ProfileImg, Service, FAQ, Message, Gallery, AboutSection, MediaConfig, Event, LinktreeLink, LinktreeConfig, Singles, Albums, Expertise, HeroAbout, Testimonials, FoundationAbout, Journey, Client
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user
import logging
logging.basicConfig(level=logging.DEBUG)


admin_messages = Blueprint(
    "admin_messages",
    __name__,
    template_folder="html",
    static_folder="scripts",
    static_url_path="/admin/static"
)

@admin_messages.route('/manage/messages')
@login_required
def manage_messages():
    from ..app import db

    messages = Message.query.order_by(Message.date.desc()).all()
    return render_template("manage_messages.html", messages=messages)


@admin_messages.route('/mark/message/read/<int:message_id>', methods=['POST'])
@login_required
def mark_message_read(message_id):
    from ..app import db
    
    message = Message.query.filter_by(
        id=message_id
    ).first_or_404()
    message.read = True
    db.session.commit()
    return {"message": "Message marked as read"}, 200

@admin_messages.route('/delete/message/<int:message_id>', methods=['POST'])
@login_required
def delete_message(message_id):
    from ..app import db

    message = Message.query.filter_by(
        id=message_id
    ).first_or_404()
    db.session.delete(message)
    db.session.commit()
    return {"message": "Message deleted"}, 200

