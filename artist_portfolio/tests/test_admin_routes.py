import pytest


def _login(client, email="admin@example.com", password="change-me-now"):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


def test_add_and_delete_skill(client):
    # login first
    r = _login(client)
    assert r.status_code == 200

    # add skill
    resp = client.post("/add skill", json={"new skill": "Guitar"})
    assert resp.status_code == 201
    assert resp.json["message"] == "skill added"
    skill = resp.json["skill"]
    assert "id" in skill

    # delete skill
    sid = skill["id"]
    resp2 = client.post(f"/delete skill/{sid}")
    assert resp2.status_code == 200
    assert resp2.json["message"] == "Skill deleted"


def test_login_form_csrf_token_allows_admin_login(client):
    import re

    client.application.config["WTF_CSRF_ENABLED"] = True
    login_page = client.get("/login")
    assert login_page.status_code == 200

    match = re.search(
        rb'name="csrf_token" value="([^"]+)"', login_page.data
    )
    assert match is not None

    response = client.post(
        "/login",
        data={
            "email": "admin@example.com",
            "password": "change-me-now",
            "csrf_token": match.group(1).decode(),
        },
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin%20dashboard")


def test_update_name_accepts_dashboard_csrf_token(client):
    import re
    from artist_portfolio.app import db
    from artist_portfolio.models import User

    _login(client)
    client.application.config["WTF_CSRF_ENABLED"] = True
    dashboard = client.get("/admin dashboard")
    assert dashboard.status_code == 200

    match = re.search(
        rb'<meta name="csrf-token" content="([^"]+)">', dashboard.data
    )
    assert match is not None
    csrf_token = match.group(1).decode()

    rejected = client.post(
        "/update name", json={"updated name": "New Artist Name"}
    )
    assert rejected.status_code == 400

    response = client.post(
        "/update name",
        json={"updated name": "New Artist Name"},
        headers={"X-CSRFToken": csrf_token},
    )
    assert response.status_code == 201
    assert response.json["message"] == "Name updated"

    with client.application.app_context():
        assert User.query.first().name == "New Artist Name"


def test_dashboard_renders_notification_helper_targets(client):
    _login(client)
    response = client.get("/admin dashboard")

    assert response.status_code == 200
    assert b'id="notification-container"' in response.data
    assert b'id="notification"' in response.data


def test_totp_login_redirects_to_admin_dashboard(client):
    import pyotp
    from artist_portfolio.app import db
    from artist_portfolio.models import Admin

    secret = pyotp.random_base32()
    with client.application.app_context():
        admin = Admin.query.filter_by(email="admin@example.com").first()
        admin_id = admin.uid
        admin.totp_secret = secret
        admin.totp_enabled = True
        db.session.commit()

    with client.session_transaction() as session:
        session["pending_admin_id"] = admin_id

    response = client.post(
        "/login/totp",
        data={"code": pyotp.TOTP(secret).now()},
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin%20dashboard")


def test_create_blog_and_service(client):
    _login(client)

    # create blog
    b = client.post(
        "/create blog",
        json={"title": "My Post", "excerpt": "Short", "content": "Full content"},
    )
    assert b.status_code == 201
    assert b.json["message"] == "Blog created"

    # create service
    s = client.post(
        "/create service",
        json={"title": "Mixing", "description": "Pro mixing service"},
    )
    assert s.status_code == 201
    assert "service" in s.json


def test_create_event_and_update_password_and_email(client):
    _login(client)

    # create event
    e = client.post(
        "/create event",
        json={"title": "Show", "date": "2026-03-01", "location": "Town Hall"},
    )
    assert e.status_code == 201
    assert e.json["message"] == "Event created"

    # update password
    pw = client.post(
        "/update password",
        json={"old_password": "change-me-now", "new_password": "newpass123"},
    )
    assert pw.status_code == 200
    assert pw.json["message"] == "password updated"

    # update email using new password
    em = client.post(
        "/update email",
        json={"password": "newpass123", "new_email": "admin2@example.com"},
    )
    assert em.status_code == 200
    assert em.json["message"] == "Email updated"


def test_add_expertise_and_testimonial_and_linktree(client):
    _login(client)

    # add expertise
    ex = client.post(
        "/add-expertise",
        json={"expertise": "Production", "desc": "Studio work", "icon": "🎧"},
    )
    assert ex.status_code == 201
    assert "exp_id" in ex.json

    # add testimonial
    t = client.post(
        "/add-testimonial",
        json={
            "artist_name": "Alex",
            "testimonial": "Great work",
            "artist_social_link": "https://twitter.com/alex",
        },
    )
    assert t.status_code == 201
    assert t.json["message"] == "New testimonial successfully added."

    # create linktree link
    l = client.post(
        "/create linktree link",
        json={"text": "Listen", "url": "https://spotify.com"},
    )
    assert l.status_code == 201
    assert l.json["message"] == "Link created successfully"


def test_upload_gallery_image_success(client):
    from io import BytesIO
    from PIL import Image

    _login(client)

    image_data = BytesIO()
    Image.new("RGB", (2, 2), color="red").save(image_data, format="PNG")
    image_data.seek(0)

    resp = client.post(
        "/upload gallery image",
        data={"image": (image_data, "test.png"), "title": "Test Image"},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 201
    assert resp.json["message"] == "Image uploaded"
    assert "item" in resp.json
    assert resp.json["item"]["title"] == "Test Image"


def test_upload_gallery_image_no_file(client):
    _login(client)

    resp = client.post("/upload gallery image", data={})
    assert resp.status_code == 400
    assert resp.json["message"] == "No file part"


def test_upload_gallery_image_invalid_type(client):
    from io import BytesIO

    _login(client)

    # Try uploading an invalid file type
    file_data = BytesIO(b"invalid content")
    file_data.seek(0)

    resp = client.post(
        "/upload gallery image",
        data={"image": (file_data, "test.txt")},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 400
    assert resp.json["message"] == "Invalid file type"


def test_upload_gallery_image_rejects_invalid_image_content(client):
    from io import BytesIO

    _login(client)
    resp = client.post(
        "/upload gallery image",
        data={"image": (BytesIO(b"not actually an image"), "spoof.png")},
        content_type="multipart/form-data",
    )

    assert resp.status_code == 400
    assert resp.json["message"] == "Uploaded file is not a valid supported image."


def test_upload_gallery_image_rejects_mismatched_extension(client):
    from io import BytesIO
    from PIL import Image

    _login(client)
    image_data = BytesIO()
    Image.new("RGB", (2, 2), color="blue").save(image_data, format="PNG")
    image_data.seek(0)

    resp = client.post(
        "/upload gallery image",
        data={"image": (image_data, "spoof.jpg")},
        content_type="multipart/form-data",
    )

    assert resp.status_code == 400
    assert resp.json["message"] == "File extension does not match image content."


def test_upload_gallery_image_rejects_oversized_file(client):
    from io import BytesIO
    from artist_portfolio.upload_validation import MAX_IMAGE_SIZE

    _login(client)
    resp = client.post(
        "/upload gallery image",
        data={"image": (BytesIO(b"x" * (MAX_IMAGE_SIZE + 1)), "large.png")},
        content_type="multipart/form-data",
    )

    assert resp.status_code == 413
    assert "8 MiB" in resp.json["message"]


def test_add_gallery_video(client):
    _login(client)

    resp = client.post(
        "/add gallery video",
        json={"url": "https://youtube.com/watch?v=test", "title": "My Video"},
    )
    assert resp.status_code == 201
    assert resp.json["message"] == "Video added"
    assert resp.json["item"]["url"] == "https://youtube.com/watch?v=test"


def test_add_gallery_video_no_url(client):
    _login(client)

    resp = client.post("/add gallery video", json={"title": "No URL"})
    assert resp.status_code == 400
    assert resp.json["message"] == "URL required"


def test_delete_gallery_item(client):
    from io import BytesIO
    from PIL import Image

    _login(client)

    # First, add a gallery item
    image_data = BytesIO()
    Image.new("RGB", (2, 2), color="green").save(image_data, format="PNG")
    image_data.seek(0)

    add_resp = client.post(
        "/upload gallery image",
        data={"image": (image_data, "delete_test.png")},
        content_type="multipart/form-data",
    )
    assert add_resp.status_code == 201
    item_id = add_resp.json["item"]["id"]

    # Now delete it
    del_resp = client.post(f"/delete gallery item/{item_id}")
    assert del_resp.status_code == 200
    assert del_resp.json["message"] == "Item deleted"


def test_create_admin_cli_requires_strong_password(client):
    from werkzeug.security import check_password_hash
    from artist_portfolio.app import db
    from artist_portfolio.models import Admin

    app = client.application
    with app.app_context():
        Admin.query.delete()
        db.session.commit()

    runner = app.test_cli_runner()
    weak_result = runner.invoke(
        args=["create-admin"],
        input="owner@example.com\nshort\nshort\n",
    )
    assert weak_result.exit_code != 0
    assert "at least 16 characters" in weak_result.output

    password = "correct-horse-battery-staple-2026"
    result = runner.invoke(
        args=["create-admin"],
        input=f"owner@example.com\n{password}\n{password}\n",
    )
    assert result.exit_code == 0
    assert "Admin account created." in result.output

    with app.app_context():
        admin = Admin.query.filter_by(email="owner@example.com").first()
        assert admin is not None
        assert check_password_hash(admin.password, password)
