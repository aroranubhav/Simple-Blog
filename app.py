from crypt import methods
from pydoc import describe
from turtle import pos
from flask import Flask, render_template, flash, request, redirect, url_for, make_response
from flask_wtf import FlaskForm
from wtforms import FormField, StringField, SubmitField, EmailField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
import os
import sys
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea

#flask instance
app = Flask(__name__)

#sqlite db config
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

#mysql db config --> mysql://username:password@localhost/db_nameex
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:AlMax579@localhost/users'

#setting up postgres
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://maxi:AlMax579@localhost:5432/users'
app.config['SECRET_KEY'] = os.urandom(32)

#initialising sqlalchemy instance
db = SQLAlchemy(app = app)

migrate = Migrate(app = app, db = db)

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(120), nullable = False, unique = True)
    job_profile = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default = datetime.utcnow)
    password_hash = db.Column(db.String(150))

    @property
    def password(self):
        raise AttributeError('Password is not in a readable format!')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password = password)
    
    def verify_password(self, password):
        return check_password_hash(pwhash = self.password_hash, password = password)

    def __repr__(self) -> str:
        return f'<Name {self.name}>'

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(250))
    content = db.Column(db.Text)
    author = db.Column(db.String(250))
    date_posted = db.Column(db.DateTime, default = datetime.utcnow)
    slug = db.Column(db.String(250))

class PostForm(FlaskForm):
    title = StringField('Title', validators = [DataRequired(message = 'This field requires a value')])
    content = StringField('Content', validators =  [DataRequired(message = 'This field requires a value')], 
        widget = TextArea())
    author = StringField('Author', validators =  [DataRequired(message = 'This field requires a value')])
    slug = StringField('Slug', validators =  [DataRequired(message = 'This field requires a value')])
    submit = SubmitField('Submit')

class NameForm(FlaskForm):
    name = StringField("What's your name?", validators = [DataRequired(message = 'This field requires a value')])
    submit = SubmitField("Submit")

class PasswordForm(FlaskForm):
    email = EmailField('Email', validators = [DataRequired(message = 'This field requires a value')])
    password = PasswordField('Password', validators = [DataRequired()])
    submit = SubmitField('Submit')

class UserForm(FlaskForm):
    name = StringField('Name', validators = [DataRequired(message = 'This field requires a value')])
    email = EmailField('Email', validators = [DataRequired(message = 'This field requires a value'), 
                                Email(message = 'Please input a vaild email address!')])
    job_profile = StringField('Job Profile')
    password = PasswordField('Password', validators = [DataRequired(), EqualTo('password_confirm',
                                message = 'Passwords must match!')])
    password_confirm = PasswordField('Confirm Password')
    submit = SubmitField('Submit')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name = name)

@app.route('/date')
def get_current_date():
    return {
        'DateTime' : datetime.now()
    }

@app.route('/name', methods = ['GET', 'POST'])
def name():
    name = None
    form = NameForm()
    #validate form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash('Form submitted successfully!')

    return render_template('name.html',
        name = name, 
        form = form)

@app.route('/test_pwd', methods = ['GET', 'POST'])
def test_pwd():
    email = None
    pwd = None
    pwd_to_check = None
    passed = None
    form = PasswordForm()
    user = None

    #validate form
    if form.validate_on_submit():
        email = form.email.data
        pwd = form.password.data
        user = Users.query.filter_by(email = email).first()

        if user is not None:
            passed = check_password_hash(pwhash = user.password_hash, password = pwd)
        else:
            passed = False

        form.email.data = ''
        form.password.data = ''

        #flash('Form submitted successfully!')  
    
    return render_template('pwd_test.html', 
        email = email, 
        password = pwd,
        user = user,
        passed = passed,
        form = form)

@app.route('/user/add', methods = ['GET', 'POST'])
def add_user():
    user_name = None
    user_form = UserForm()

    if user_form.validate_on_submit():
        user_name = user_form.name.data
        user_email = user_form.email.data
        job_profile = user_form.job_profile.data
        user_pwd = user_form.password.data
        user = Users.query.filter_by(email = user_email).first()
        if user is None:
            #hashed_pwd = generate_password_hash(user_pwd, "sha256")
            user = Users(name = user_name, email = user_email,
                    job_profile = job_profile)
            #using password setter property to set the user password
            user.password = user_pwd
            db.session.add(user) 
            db.session.commit() 
            user_form.name.data = ''
            user_form.email.data = ''
            user_form.job_profile.data = ''
            user_form.password.data = ''
            flash('User {} with email: {} added successfully!'.format(user_name, user_email))
    
    all_users = Users.query.order_by(Users.date_added)

    return render_template('add_user.html',
        name = user_name, 
        form = user_form,
        users = all_users)

@app.route('/update/<user_id>', methods = ['GET', 'POST'])
def update_user(user_id):
    form = UserForm()
    updated_user = Users.query.get_or_404(user_id)
    if request.method == 'POST':
        updated_user.name = request.form['name']
        updated_user.email = request.form['email']
        updated_user.job_profile = request.form['job_profile']
        try:
            db.session.commit()
            flash('User updated successfully!')
            return render_template('update_user.html', 
                form = form,
                updated_user = updated_user)
        except:
            db.session.rollback()
            flash('Error! Failed to update the user!')
            return render_template('update_user.html', 
                form = form,
                updated_user = updated_user)
        finally:
            db.session.close()
    else:
        return render_template('update_user.html', 
                form = form,
                updated_user = updated_user)

@app.route('/delete/<user_id>')
def delete_user(user_id):
    error = False
    try:
        user = Users.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
    except:
        error = True
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()

    if error:
        flash('An error occured while deleting the user.')
    else:
        flash('Successfully deleted the user.')

    return redirect(url_for('add_user'))

@app.route('/add-post', methods = ['GET', 'POST'])
def add_post():
    form = PostForm()

    try:
        if form.validate_on_submit():
            post = Posts()
            form.populate_obj(post)
            #clearing the form
            form.title.data = ''
            form.author.data = ''
            form.content.data = ''
            form.slug.data = ''
            #adding post to db
            db.session.add(post)
            db.session.commit()
            flash('Blog Post submitted successfully!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('There was an error creating the Blog Post.')
    finally:
        db.session.close()
    
    return render_template('add_post.html', 
            form = form)

@app.route('/blog-posts', methods = ['GET'])
def get_blog_posts():
    try:
        posts = Posts.query.all()
    except:
        print(sys.exc_info())
    return render_template('blog_posts.html', 
            posts = posts)


#page not found handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

#internal server error handler
@app.errorhandler(500)
def internal_server_handler(e):
    return render_template('500.html'), 500