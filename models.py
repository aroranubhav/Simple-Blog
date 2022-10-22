from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    user_name = db.Column(db.String(20), nullable = False, unique = True)
    email = db.Column(db.String(120), nullable = False, unique = True)
    job_profile = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default = datetime.utcnow)
    password_hash = db.Column(db.String(150))
    posts = db.relationship('Posts', backref = 'user', lazy = True)

    @property
    def password(self):
        raise AttributeError('Password is not in a readable format!')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password = password)
    
    def verify_password(self, password):
        return check_password_hash(pwhash = self.password_hash, password = password)

    def __repr__(self) -> str:
        return f'<Name {self.name}> Username {self.user_name} Email {self.email} Password {self.password_hash}'

class Posts(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(250))
    content = db.Column(db.Text)
    #author = db.Column(db.String(250))
    date_posted = db.Column(db.DateTime, default = datetime.utcnow)
    slug = db.Column(db.String(250))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))