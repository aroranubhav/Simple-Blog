from flask import Flask, render_template, flash, request, redirect, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
import sys
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, current_user, LoginManager, login_required
from webforms import LoginForm, PostForm, UserForm, NameForm, PasswordForm

#flask instance
app = Flask(__name__)
app.config.from_object('config')

#initialising sqlalchemy instance
db = SQLAlchemy(app = app)

#initialising migrate library
migrate = Migrate(app = app, db = db)

#setting up login manager
login_manager = LoginManager()
login_manager.init_app(app = app)
login_manager.login_view = 'login'

from models import Users, Posts

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(user_name = form.user_name.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user = user)
                flash('You are successfully logged in!')
                return redirect(url_for('dashboard'))
            else:
                flash('Please check the password you have entered and try again!')
        else:
            flash('Username you have entered does not exist, try again!')

    return render_template('login.html',
        form = form)

@app.route('/logout', methods = ['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You have been successfully logged out.')
    return redirect(url_for('login'))

@app.route('/dashboard', methods = ['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    user_id = current_user.id
    updated_user = Users.query.get_or_404(user_id)
    if updated_user and request.method == 'POST':
        #form.populate_obj(updated_user)
        updated_user.name = request.form['name']
        updated_user.user_name = request.form['user_name']
        updated_user.email = request.form['email']
        updated_user.job_profile = request.form['job_profile']
        try:
            db.session.commit()
            flash('User updated successfully!')
            return render_template('dashboard.html', 
                form = form,
                updated_user = updated_user)
        except:
            db.session.rollback()
            flash('Error! Failed to update the user!')
            return render_template('dashboard.html', 
                form = form,
                updated_user = updated_user)
        finally:
            db.session.close()
    else:
        if not user:
            flash('Sorry could not find the user!!')
        else:
            return render_template('dashboard.html', 
                form = form, 
                updated_user = updated_user)

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
    name = None
    user_form = UserForm()

    if user_form.validate_on_submit():
        name = user_form.name.data
        user_name = user_form.user_name.data
        user_email = user_form.email.data
        job_profile = user_form.job_profile.data
        user_pwd = user_form.password.data
        user = Users.query.filter_by(email = user_email).first()
        if user is None:
            #hashed_pwd = generate_password_hash(user_pwd, "sha256")
            user = Users(name = name, user_name = user_name, email = user_email,
                    job_profile = job_profile)
            #using password setter property to set the user password
            user.password = user_pwd
            db.session.add(user) 
            db.session.commit() 
            user_form.name.data = ''
            user_form.user_name.data = ''
            user_form.email.data = ''
            user_form.job_profile.data = ''
            user_form.password.data = ''
            flash('User {} with email: {} added successfully!'.format(user_name, user_email))
    
    all_users = Users.query.order_by(Users.date_added)

    return render_template('add_user.html',
        name = name, 
        form = user_form,
        users = all_users)

@app.route('/update/<user_id>', methods = ['GET', 'POST'])
@login_required
def update_user(user_id):
    form = UserForm()
    user_id = int(user_id)
    updated_user = Users.query.get_or_404(user_id)
    if request.method == 'POST':
        #form.populate_obj(updated_user)
        updated_user.name = request.form['name']
        updated_user.user_name = request.form['user_name']
        updated_user.email = request.form['email']
        updated_user.job_profile = request.form['job_profile']
        try:
            db.session.commit()
            flash('User updated successfully!')
            return render_template('update_user.html', 
                form = form,
                updated_user = updated_user,
                user_id = user_id)
        except:
            db.session.rollback()
            flash('Error! Failed to update the user!')
            return render_template('update_user.html', 
                form = form,
                updated_user = updated_user,
                user_id = user_id)
        finally:
            db.session.close()
    else:
        return render_template('update_user.html', 
                form = form,
                updated_user = updated_user, 
                user_id = user_id)

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
            post.user_id = current_user.id
            #clearing the form
            form.title.data = ''
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

@app.route('/blog-posts')
def get_blog_posts():
    try:
        posts = Posts.query.order_by(Posts.date_posted).all()
    except:
        print(sys.exc_info())
    return render_template('blog_posts.html', 
            posts = posts)

@app.route('/posts/<int:post_id>')
def get_post(post_id):
    post = Posts.query.get_or_404(post_id)
    return render_template('blog_post.html', post = post)

@app.route('/posts/edit/<int:post_id>', methods = ['GET', 'POST'])
@login_required
def edit_blog_post(post_id):
    print(post_id)
    post = Posts.query.get_or_404(post_id)
    form = PostForm()
    
    if form.validate_on_submit():
        form.populate_obj(post)
        db.session.add(post)
        db.session.commit()
        flash('Blog post updated successfully!')
        return redirect(url_for('get_post', post_id = post.id))
    
    form.title.data = post.title
    form.slug.data = post.slug
    form.content.data = post.content

    return render_template('edit_blog_post.html',
        form = form, 
        post = post)

@app.route('/posts/delete/<int:post_id>')
def delete_blog_post(post_id):
    post = Posts.query.get_or_404(post_id)

    try:
        db.session.delete(post)
        db.session.commit()
        flash('Blog post deleted successfully!')
    except:
        db.session.rollback()
        flash('An Error occurred while deleting the post!')
    finally:
        db.session.close()
   
    return redirect(url_for('get_blog_posts'))

#page not found handler
@app.errorhandler(404) 
def page_not_found(e):
    return render_template('404.html'), 404

#internal server error handler
@app.errorhandler(500)
def internal_server_handler(e):
    return render_template('500.html'), 500