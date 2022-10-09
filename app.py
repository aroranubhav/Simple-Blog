from crypt import methods
from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import FormField, StringField, SubmitField
from wtforms.validators import DataRequired
import os

#flask instance
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)

class NameForm(FlaskForm):
    name = StringField("What's your name?", validators = [DataRequired()])
    submit = SubmitField("Submit")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name = name)

#page not found handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

#internal server error handler
@app.errorhandler(500)
def internal_server_handler(e):
    return render_template('500.html'), 500

@app.route('/name', methods = ['GET', 'POST'])
def name():
    name = None
    form = NameForm()
    #validate form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''

    return render_template('name.html',
            name = name, 
            form = form)