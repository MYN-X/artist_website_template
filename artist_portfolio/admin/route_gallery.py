from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user
import cloudinary.uploader
import logging

from ..models import Admin, User, Skills, Blog, ProfileImg, Service, FAQ, Message, Gallery
from ..database.login import AdminLogin
from ..upload_validation import validate_image_upload

logging.basicConfig(level=logging.DEBUG)

admin_gallery = Blueprint(
    "admin_gallery",
    __name__,
    template_folder="html",
    static_folder="scripts",
    static_url_path="/admin/static"
)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_gallery.route('/manage/gallery')
@login_required
def manage_gallery():
    images = Gallery.query.filter_by(type='image').order_by(Gallery.id).all()
    videos = Gallery.query.filter_by(type='video').order_by(Gallery.id).all()

    return render_template(
        "manage_gallery.html",
        images=images,
        videos=videos
    )


@admin_gallery.route('/upload/gallery/image', methods=['POST'])
@login_required
def upload_gallery_image():
    from ..app import db

    images_count = Gallery.query.filter_by(type='image').count()
    if images_count >= 5:
        return {"message": "Maximum 5 images allowed. Delete an old image first."}, 400

    if 'image' not in request.files:
        return {"message": "No file part"}, 400

    file = request.files['image']

    if file.filename == '':
        return {"message": "No selected file"}, 400

    if file and allowed_file(file.filename):
        validation_error, status_code = validate_image_upload(file)
        if validation_error:
            return {"message": validation_error}, status_code

        try:
            upload_result = cloudinary.uploader.upload(
                file,
                folder="gallery_images_oom_dass"
            )
        except Exception:
            logging.exception("Gallery image upload failed")
            return {"message": "Upload failed."}, 500

        image_url = upload_result.get("secure_url")
        public_id = upload_result.get("public_id")

        title = request.form.get('title', '')

        new_item = Gallery(
            type='image',
            url=public_id,
            cloud_url=image_url,
            title=title
        )

        db.session.add(new_item)
        db.session.commit()

        return {
            "message": "Image uploaded",
            "item": {
                "id": new_item.id,
                "url": new_item.cloud_url,
                "title": new_item.title
            }
        }, 201

    return {"message": "Invalid file type"}, 400


@admin_gallery.route('/delete/gallery/item/<int:item_id>', methods=['POST'])
@login_required
def delete_gallery_item(item_id):
    from ..app import db

    item = Gallery.query.filter_by(id=item_id).first_or_404()

    if item.type == 'image':
        if item.url:  # this is public_id now
            try:
                cloudinary.uploader.destroy(item.url)
            except Exception as e:
                print(f"Warning: Failed to delete image: {e}")

    db.session.delete(item)
    db.session.commit()

    return {"message": "Item deleted"}, 200

@admin_gallery.route('/add/gallery/video', methods=['POST'])
@login_required
def add_gallery_video():
    from ..app import db
    data = request.get_json()
    print(data)
    url = data.get('url')
    title = data.get('title', '')
    if not url:
        return {"message": "URL required"}, 400
    new_item = Gallery(
        type='video',
        url=url,
        title=title,
        cloud_url=''  # no cloud URL for videos, but keeping field for consistency
    )
    db.session.add(new_item)
    db.session.commit()
    return {"message": "Video added", "item": {"id": new_item.id, "url": new_item.url, "title": new_item.title}}, 201

