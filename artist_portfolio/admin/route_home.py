from pathlib import Path
from ..models import Admin, User, Skills, Blog, ProfileImg, Service, FAQ, Message, Gallery, AboutSection, MediaConfig, Event, LinktreeLink, LinktreeConfig, Singles, Albums, Expertise, HeroAbout, Testimonials, FoundationAbout, Journey, Client
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user
from ..upload_validation import validate_image_upload
import cloudinary.uploader
from .config import init_cloudinary
import logging
logging.basicConfig(level=logging.DEBUG)

init_cloudinary()



admin_home = Blueprint(
    "admin_home",
    __name__,
    template_folder="html",
    static_folder="scripts",
    static_url_path="/admin/static"
)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_home.route('/admin/dashboard')
@login_required
def admin_dashboard():
    from ..app import db
    skills = Skills.query.all()
    logging.debug([s.skill for s in skills])
    return render_template("admin_dashboard.html", skills=skills)


@admin_home.route('/save/update/ga4', methods=['POST'])
@login_required
def save_update_ga4():
    from ..app import db
    
    data = request.get_json() or request.form

    name = (data.get("name") or "").strip()
    ga4_measurement_id = (data.get("ga4_measurement_id") or "").strip()

    if not name:
        return jsonify({
            "success": False,
            "message": "Name is required."
        }), 400

    if not ga4_measurement_id:
        return jsonify({
            "success": False,
            "message": "GA4 Measurement ID is required."
        }), 400

    if not ga4_measurement_id.startswith("G-"):
        return jsonify({
            "success": False,
            "message": "Invalid GA4 Measurement ID. It should start with 'G-'."
        }), 400

    try:
        client = Client.query.filter_by(name=name).first()

        if client:
            client.ga4_measurement_id = ga4_measurement_id
            message = "GA4 Measurement ID updated successfully."
        else:
            client = Client(
                name=name,
                ga4_measurement_id=ga4_measurement_id
            )
            db.session.add(client)
            message = "GA4 Measurement ID saved successfully."

        db.session.commit()

        return jsonify({
            "success": True,
            "message": message,
            "client": {
                "id": client.id,
                "name": client.name,
                "ga4_measurement_id": client.ga4_measurement_id
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "An error occurred while saving GA4 data.",
            "error": str(e)
        }), 500
    
@admin_home.route('/update/name', methods=['POST'])
@login_required
def upadte_name():
    from ..app import db
    
    data = request.get_json()
    # Only update current artist's user record
    user = User.query.first()
    if user:
        user.name = data['updated name']
        db.session.commit()
        logging.debug("Name has been updated")
        return {"message": "Name updated"}, 201
    else:
        return {"message": "User not found"}, 404

@admin_home.route('/update/password', methods=['POST'])
@login_required
def update_password():
    
    data = request.get_json()
    from ..app import db
    logging.debug(data)
    
    # admin_user = current_user
    admin_user = Admin.query.first()
    
    # if not admin_user.artist_id:
    #     return {"message": "Error - Admin not properly configured"}, 400
    
    if not check_password_hash(admin_user.password, data.get("old_password")):
        return {"message": "Error - passwords don't match"}, 401

    password = generate_password_hash(data.get("new_password"))
    admin_user.password = password
    db.session.commit()

    return {"message": "password updated"}, 200

@admin_home.route('/update/email', methods=['POST'])
@login_required
def update_email():
    from flask_login import current_user
    from ..app import db
    data = request.get_json()
    logging.debug(data)
    # admin_user = current_user
    admin_user = Admin.query.first()

    
    if not check_password_hash(admin_user.password, data.get("password")):
        return {"message": "Error - please enter correct password."}, 401
    
    # Check if new email already exists
    existing = Admin.query.filter_by(email=data.get('new_email')).first()
    if existing and existing.uid != admin_user.uid:
        return {"message": "Email already in use"}, 409
    
    admin_user.email = data.get('new_email')
    db.session.commit()
    return {'message': 'Email updated'}, 200

@admin_home.route('/update/about', methods=['POST'])
@login_required
def update_user_about():
    from ..app import db
    
    data = request.get_json()
    # Only update current artist's user record
    user = User.query.first()
    if user:
        user.short_about = data.get('updated about')
        db.session.commit()
        return {"message": "About has been updated"}, 200
    return {"message": "User not found"}, 404

@admin_home.route('/add/skill', methods=['POST'])
@login_required
def add_new_skill():
    from ..app import db
    
    data = request.get_json()
   
    skill = Skills(
        skill=data.get('new skill')
    )
    db.session.add(skill)
    db.session.commit()
    logging.debug(data)
    return {"message": "skill added", "skill": {"id": skill.id, "skill": skill.skill}}, 201

@admin_home.route('/delete/skill/<int:skill_id>', methods=['POST'])
@login_required
def delete_skill(skill_id):
    from ..app import db
    
    skill = Skills.query.filter_by(
        id=skill_id
    ).first_or_404()
    db.session.delete(skill)
    db.session.commit()
    return {"message": "Skill deleted"}, 200

@admin_home.route('/update/profile/picture', methods=['POST'])
@login_required
def update_profile_picture():
    from ..app import db

    if 'profile_picture' not in request.files:
        return {"message": "No file part"}, 400

    file = request.files['profile_picture']

    if file.filename == '':
        return {"message": "No selected file"}, 400

    if file and allowed_file(file.filename):
        validation_error, status_code = validate_image_upload(file)
        if validation_error:
            return {"message": validation_error}, status_code

        # Upload to Cloudinary
        try:
            upload_result = cloudinary.uploader.upload(
                file,
                folder="profile_pictures_oom_dass"
            )
        except Exception:
            logging.exception("Profile picture upload failed")
            return {"message": "Upload failed."}, 500

        image_url = upload_result.get("secure_url")
        public_id = upload_result.get("public_id")

        user = ProfileImg.query.first()

        if user:
            old_public_id = user.profile_picture  # store public_id now

            user.profile_picture = public_id
            user.profile_picture_url = image_url
              # <-- ADD THIS COLUMN
            if old_public_id:
                try:
                    cloudinary.uploader.destroy(old_public_id)
                except Exception as e:
                    print(f"Warning: Failed to delete old image: {e}")

            db.session.commit()

            return {"message": "Profile picture updated", "url": image_url}, 200

        else:
            user = ProfileImg(
                id=1,
                profile_picture=public_id,
                profile_picture_url=image_url
            )
            db.session.add(user)
            db.session.commit()

            return {"message": "Profile picture updated", "url": image_url}, 200

    return {"message": "Invalid file type"}, 400

@admin_home.route('/update/banner/picture', methods=['POST'])
@login_required
def update_banner_picture():
    from ..app import db

    if 'banner_picture' not in request.files:
        return {"message": "No file part"}, 400
    
    file = request.files['banner_picture']

    if file.filename == '':
        return {"message": "No selected file"}, 400
    
    if file and allowed_file(file.filename):
        validation_error, status_code = validate_image_upload(file)
        if validation_error:
            return {"message": validation_error}, status_code
        # Upload to Cloudinary
        try:
            upload_result = cloudinary.uploader.upload(
                file,
                folder="profile_pictures_oom_dass"
            )
        except Exception:
            logging.exception("Banner picture upload failed")
            return {"message": "Upload failed."}, 500

        image_url = upload_result.get("secure_url")
        public_id = upload_result.get("public_id")

        user = ProfileImg.query.first()

        if user:
            old_public_id = user.banner_img  # store public_id now

            user.banner_img = public_id
            user.banner_picture_url = image_url

            if old_public_id:
                try:
                    cloudinary.uploader.destroy(old_public_id)
                except Exception as e:
                    print(f"Warning: Failed to delete old image: {e}")

            db.session.commit()

            return {"message": "Banner picture updated", "url": image_url}, 200

        else:
            user = ProfileImg(
                id=1,
                banner_img=public_id,
                banner_picture_url=image_url
            )
            db.session.add(user)
            db.session.commit()

            return {"message": "Banner picture updated", "url": image_url}, 200

    return {"message": "Invalid file type"}, 400

