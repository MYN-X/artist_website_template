from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from ..database.login import AdminLogin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user
from datetime import datetime
import logging

from ..models import Event

admin_events = Blueprint(
    "admin_events",
    __name__,
    template_folder="html",
    static_folder="scripts",
    static_url_path="/admin/static"
)

@admin_events.route('/manage/events')
@login_required
def manage_events():
    from ..app import db
    
    events = Event.query.order_by(Event.date).all()
    return render_template("manage_events.html", events=events)


@admin_events.route('/create/event', methods=['POST'])
@login_required
def create_event():
    from ..app import db
    

    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    date_str = data.get('date')  # YYYY-MM-DD
    time_str = data.get('time')  # HH:MM
    location = data.get('location')
    image_url = data.get('image_url', '')
    
    if not title or not date_str:
        return {"message": "Title and date required"}, 400
    
    try:
        event_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        event_time = None
        if time_str:
            event_time = datetime.strptime(time_str, '%H:%M').time()
        
        new_event = Event(
            title=title,
            description=description,
            date=event_date,
            time=event_time,
            location=location,
            image_url=image_url
        )
        db.session.add(new_event)
        db.session.commit()
        return {"message": "Event created", "event": {"id": new_event.id, "title": new_event.title, "date": new_event.date.isoformat()}}, 201
    except Exception as e:
        db.session.rollback()
        return {"message": f"Error creating event: {str(e)}"}, 500

@admin_events.route('/edit/event/<int:event_id>', methods=['POST'])
@login_required
def edit_event(event_id):
    from ..app import db
    from datetime import datetime
    
    event = Event.query.filter_by(
        id=event_id
    ).first_or_404()
    data = request.get_json()
    
    try:
        if 'title' in data:
            event.title = data['title']
        if 'description' in data:
            event.description = data['description']
        if 'date' in data:
            event.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        if 'time' in data and data['time']:
            event.time = datetime.strptime(data['time'], '%H:%M').time()
        if 'location' in data:
            event.location = data['location']
        if 'image_url' in data:
            event.image_url = data['image_url']
        
        db.session.commit()
        return {"message": "Event updated"}, 200
    except Exception as e:
        db.session.rollback()
        return {"message": f"Error updating event: {str(e)}"}, 500

@admin_events.route('/delete/event/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    from ..app import db
   
    event = Event.query.filter_by(
        id=event_id
    ).first_or_404()
    db.session.delete(event)
    db.session.commit()
    return {"message": "Event deleted"}, 200


