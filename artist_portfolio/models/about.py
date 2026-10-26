from ..extensions import db

class AboutSection(db.Model):
    __tablename__ = 'about_section'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    section_name = db.Column(db.Text, nullable=False)
    title = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=True)  # JSON string for complex data
    order = db.Column(db.Integer, nullable=False, default=0)


class HeroAbout(db.Model): 
    __tablename__ = "hero_about"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    hero_title = db.Column(db.Text, nullable=False)
    hero_brief  = db.Column(db.Text, nullable=False)

class FoundationAbout(db.Model):
    __tablename__ = "foundation_about"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.Text, nullable=False)
    paragraphs = db.Column(db.Text, nullable=False)


class Journey(db.Model):
    __tablename__ = "journey"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    desc = db.Column(db.Text, nullable=False)
    
class Expertise(db.Model):
    __tablename__ = 'expertise'

    exp_id = db.Column(db.Integer, primary_key=True, nullable=False)
    expertise = db.Column(db.Text, nullable=False)
    desc = db.Column(db.Text, nullable=False)
    icon = db.Column(db.Text, nullable=False)

class Testimonials(db.Model):
    __tablename__ = "testimonials"

    t_id = db.Column(db.Integer, primary_key=True, nullable=False)
    artist_name = db.Column(db.Text, nullable=False)
    testimonial = db.Column(db.Text, nullable=False)
    artist_social = db.Column(db.Text, nullable=False)
