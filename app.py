from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import FormField, StringField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
import os

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

    def __repr__(self) -> str:
        return f'<Name {self.name}>'

class NameForm(FlaskForm):
    name = StringField("What's your name?", validators = [DataRequired(message = 'This field requires a value')])
    submit = SubmitField("Submit")

class UserForm(FlaskForm):
    name = StringField('Name', validators = [DataRequired(message = 'This field requires a value')])
    email = EmailField('Email', validators = [DataRequired(message = 'This field requires a value'), 
                                Email(message = 'Please input a vaild email address!')])
    job_profile = StringField('Job Profile')
    submit = SubmitField('Submit')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name = name)

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

@app.route('/user/add', methods = ['GET', 'POST'])
def add_user():
    user_name = None
    user_form = UserForm()

    if user_form.validate_on_submit():
        user_name = user_form.name.data
        user_email = user_form.email.data
        job_profile = user_form.job_profile.data
        user = Users.query.filter_by(email = user_email).first()
        if user is None:
            users = Users(name = user_name, email = user_email, job_profile = job_profile)
            db.session.add(users)
            db.session.commit() 
            user_form.name.data = ''
            user_form.email.data = ''
            user_form.job_profile.data = ''
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

#page not found handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

#internal server error handler
@app.errorhandler(500)
def internal_server_handler(e):
    return render_template('500.html'), 500