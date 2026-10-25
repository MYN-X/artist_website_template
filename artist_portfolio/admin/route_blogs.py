from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from ..models import Admin, User, Skills, Blog, ProfileImg, Service, FAQ, Message, Gallery, AboutSection, MediaConfig, Event, LinktreeLink, LinktreeConfig, Singles, Albums, Expertise, HeroAbout, Testimonials, FoundationAbout, Journey, Client
from flask_login import login_user, login_required, current_user
import logging
logging.basicConfig(level=logging.DEBUG)

admin_blogs = Blueprint(
    "admin_blogs",
    __name__,
    template_folder="html",
    static_folder="scripts",
    static_url_path="/admin/static"
)


@admin_blogs.route('/manage/blogs')
@login_required
def manage_blogs():
    from ..app import db

    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=2, type=int)

    per_page = max(1, min(per_page, 2))
    page = max(1, page)

    pagination = (
        Blog.query
        .order_by(Blog.date.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    
    blogs = pagination.items
    return render_template("manage_blogs.html", blogs=blogs, pagination=pagination)

@admin_blogs.route('/create/blog', methods=['POST'])
@login_required
def create_blog():
    from ..app import db
    # from flask import g
    data = request.get_json()
    title = data.get('title')
    excerpt = data.get('excerpt')
    content = data.get('content')
    if not title or not excerpt or not content:
        return {"message": "All fields required"}, 400
    # MULTI-TENANT SAFE: Always set artist_id from context
    new_blog = Blog(
        title=title,
        excerpt=excerpt,
        content=content
    )
    db.session.add(new_blog)
    db.session.commit()
    return {"message": "Blog created"}, 201

@admin_blogs.route('/edit/blog/<int:blog_id>', methods=['POST'])
@login_required
def edit_blog(blog_id):
    from ..app import db
    # from flask import g
    blog = Blog.query.filter_by(
        id=blog_id
    ).first_or_404()
    data = request.get_json()
    blog.title = data.get('title', blog.title)
    blog.excerpt = data.get('excerpt', blog.excerpt)
    blog.content = data.get('content', blog.content)
    db.session.commit()
    return {"message": "Blog updated"}, 200

@admin_blogs.route('/delete/blog/<int:blog_id>', methods=['POST'])
@login_required
def delete_blog(blog_id):
    from ..app import db
    # from flask import g
   
    blog = Blog.query.filter_by(
        id=blog_id
    ).first_or_404()
    db.session.delete(blog)
    db.session.commit()
    return {"message": "Blog deleted"}, 200

