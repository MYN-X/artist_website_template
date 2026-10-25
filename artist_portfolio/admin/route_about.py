from pathlib import Path
from ..models import Admin, User, Skills, Blog, ProfileImg, Service, FAQ, Message, Gallery, AboutSection, MediaConfig, Event, LinktreeLink, LinktreeConfig, Singles, Albums, Expertise, HeroAbout, Testimonials, FoundationAbout, Journey, Client
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user
import logging
logging.basicConfig(level=logging.DEBUG)


admin_about = Blueprint(
    "admin_about",
    __name__,
    template_folder="html",
    static_folder="scripts",
    static_url_path="/admin/static"
)

@admin_about.route('/manage/about')
@login_required
def manage_about():
    from ..app import db
    import json
    from types import SimpleNamespace

    raw_sections = AboutSection.query.order_by(AboutSection.order).all()

    # Build a wrapper that supports both index access (sections[0]) and
    # attribute/get access (sections.hero, sections.get('foundation')).
    class SectionsWrapper:
        def __init__(self, rows):
            self._list = []
            self._map = {}
            for r in rows:
                # parse JSON content if possible
                parsed = {}
                if r.content:
                    try:
                        parsed = json.loads(r.content)
                    except Exception:
                        parsed = r.content

                # store a mapping-friendly dict for get-style access
                self._map[r.section_name] = {"title": r.title, "content": parsed}

                # store a simple namespace for index-based access used in template
                self._list.append(SimpleNamespace(title=r.title, content=parsed))

        def __getattr__(self, name):
            if name in self._map:
                return self._map[name]
            raise AttributeError(name)

        def __getitem__(self, idx):
            return self._list[idx]

        def get(self, key, default=None):
            return self._map.get(key, default)


    foundation = FoundationAbout.query.order_by(FoundationAbout.id.asc()).first()
    hero = HeroAbout.query.order_by(HeroAbout.id.asc()).first()

    expertise = Expertise.query.all()
    testimonials = Testimonials.query.all()

    journey_items = Journey.query.order_by(Journey.year.asc()).all()

    sections = SectionsWrapper(raw_sections)
    return render_template("manage_about.html", sections=sections, expertise=expertise, testimonials=testimonials, hero=hero, foundation=foundation, journey_items=journey_items)


@admin_about.route('/update/about/section', methods=['POST'])
@login_required
def update_about_section():
    from ..app import db
    data = request.get_json()
    section_name = data.get('section_name')
    title = data.get('title')
    content = data.get('content')  # JSON string

    logging.debug(data)

    section = AboutSection.query.filter_by(
        section_name=section_name
    ).first()
    if not section:
        section = AboutSection(
            section_name=section_name
        )
        db.session.add(section)
    section.title = title
    section.content = content
    db.session.commit()
    return {"message": "About section updated"}, 200

@admin_about.route("/hero", methods=["POST"])
@login_required
def upsert_hero():
    from ..app import db

    data = request.get_json() or {}
    hero_title = (data.get("hero-title") or "").strip()
    hero_brief = (data.get("hero-brief") or "").strip()

    if not hero_title:
        return {"message": "Error - Please provide hero title"}, 400
    if not hero_brief:
        return {"message": "Error - Please provide hero brief"}, 400

    hero = HeroAbout.query.order_by(HeroAbout.id.asc()).first()

    if not hero:
        hero = HeroAbout(hero_title=hero_title, hero_brief=hero_brief)
        db.session.add(hero)
        db.session.commit()
        return {
            "message": "About hero section successfully created.",
            "hero": {"id": hero.id, "hero_title": hero.hero_title, "hero_brief": hero.hero_brief}
        }, 201

    hero.hero_title = hero_title
    hero.hero_brief = hero_brief
    db.session.commit()

    return {
        "message": "About hero section successfully updated.",
        "hero": {"id": hero.id, "hero_title": hero.hero_title, "hero_brief": hero.hero_brief}
    }, 200


@admin_about.route("/foundation", methods=["POST"])
@login_required
def upsert_foundation():
    from ..app import db

    data = request.get_json() or {}
    paragraphs_arr = data.get("paragraphsArr") or []

    # Safely grab the two paragraphs (default to empty string)
    p1 = (paragraphs_arr[0] if len(paragraphs_arr) > 0 else "") or ""
    p2 = (paragraphs_arr[1] if len(paragraphs_arr) > 1 else "") or ""
    p1, p2 = p1.strip(), p2.strip()

    # Check if table is empty
    table_empty = db.session.query(FoundationAbout.id).first() is None

    if table_empty:
        # Insert two rows
        db.session.add_all([
            FoundationAbout(id=1, title="paragraph_one", paragraphs=p1),
            FoundationAbout(id=2, title="paragraph_two", paragraphs=p2),
        ])
        db.session.commit()
        return {"message": "Foundation section successfully created."}, 201

    # Table has data -> update existing rows; create if missing
    row1 = FoundationAbout.query.get(1)
    row2 = FoundationAbout.query.get(2)

    if row1 is None:
        row1 = FoundationAbout(id=1, title="paragraph_one", paragraphs=p1)
        db.session.add(row1)
    else:
        row1.title = "paragraph_one"
        row1.paragraphs = p1

    if row2 is None:
        row2 = FoundationAbout(id=2, title="paragraph_two", paragraphs=p2)
        db.session.add(row2)
    else:
        row2.title = "paragraph_two"
        row2.paragraphs = p2

    db.session.commit()
    return {"message": "Foundation section successfully updated."}, 200

@admin_about.route('/add/expertise', methods=['POST'])
@login_required
def add_experitse():
    from ..app import db

    data = request.get_json()

    if not data.get('expertise'):
        return {"message": "Please provide expertise title"}, 400
    expertise = data.get('expertise')

    if not data.get('desc'):
        return {"message": "Please provide expertise description"}, 400
    desc = data.get('desc')

    if not data.get('icon'):
        return {"message": "Please provide an icon"}, 400
    icon = data.get('icon')

    new_expertise = Expertise(
        expertise=expertise,
        desc=desc,
        icon=icon
    )

    db.session.add(new_expertise)
    db.session.commit()

    return {
        "message": f"'{expertise}' added successfully.",
        "exp_id": new_expertise.exp_id,
        "expertise": new_expertise.expertise,
        "desc": new_expertise.desc,
        "icon": new_expertise.icon,
    }, 201

@admin_about.route('/delete/expertise/<int:exp_id>', methods=['DELETE'])
@login_required
def delete_expertise(exp_id):
    from ..app import db

    exp = Expertise.query.get(exp_id)
    if not exp:
        return {"message": "Expertise not found."}, 404

    db.session.delete(exp)
    db.session.commit()
    return {"message": "Expertise deleted successfully.", "exp_id": exp_id}, 200

@admin_about.route('/add/testimonial', methods=['POST'])
@login_required
def add_testimonial():
    from ..app import db

    data = request.get_json() or {}

    if not data.get('artist_name'):
        return {'message': 'Please provide artist name'}, 400
    artist_name = data.get('artist_name')

    if not data.get('testimonial'):
        return {'message': 'Please provide testimonial'}, 400
    testimonial = data.get('testimonial')

    if not data.get('artist_social_link'):
        return {"message": "Please provide artist social link"}, 400
    artist_social = data.get('artist_social_link')

    new_testimonial = Testimonials(
        artist_name=artist_name,
        testimonial=testimonial,
        artist_social=artist_social
    )

    db.session.add(new_testimonial)
    db.session.commit()

    return {
        "message": "New testimonial successfully added.",
        "t_id": new_testimonial.t_id,
        "artist_name": new_testimonial.artist_name,
        "testimonial": new_testimonial.testimonial,
        "artist_social": new_testimonial.artist_social
    }, 201

@admin_about.route('/delete/testimonial/<int:t_id>', methods=['DELETE'])
@login_required
def delete_testimonial(t_id):
    from ..app import db

    t = Testimonials.query.get(t_id)
    if not t:
        return {"message": "Testimonial not found."}, 404

    db.session.delete(t)
    db.session.commit()
    return {"message": "Testimonial deleted successfully.", "t_id": t_id}, 200

@admin_about.route("/journey", methods=["POST"])
@login_required
def create_journey():
    from ..app import db

    data = request.get_json() or {}
    year = data.get("year")
    desc = (data.get("desc") or "").strip()

    try:
        year = int(year)
    except (TypeError, ValueError):
        return {"message": "Year must be an integer."}, 400

    if not desc:
        return {"message": "Description is required."}, 400

    item = Journey(year=year, desc=desc)
    db.session.add(item)
    db.session.commit()

    return {
        "message": "Journey item created.",
        "journey": {"id": item.id, "year": item.year, "desc": item.desc}
    }, 201

@admin_about.route("/journey/<int:item_id>", methods=["PUT"])
@login_required
def update_journey(item_id):
    from ..app import db

    item = Journey.query.get(item_id)
    if not item:
        return {"message": "Journey item not found."}, 404

    data = request.get_json() or {}
    year = data.get("year")
    desc = (data.get("desc") or "").strip()

    try:
        year = int(year)
    except (TypeError, ValueError):
        return {"message": "Year must be an integer."}, 400

    if not desc:
        return {"message": "Description is required."}, 400

    item.year = year
    item.desc = desc
    db.session.commit()

    return {
        "message": "Journey item updated.",
        "journey": {"id": item.id, "year": item.year, "desc": item.desc}
    }, 200

@admin_about.route("/journey/<int:item_id>", methods=["DELETE"])
@login_required
def delete_journey(item_id):
    from ..app import db

    item = Journey.query.get(item_id)
    if not item:
        return {"message": "Journey item not found."}, 404

    db.session.delete(item)
    db.session.commit()

    return {"message": "Journey item deleted.", "id": item_id}, 200




