from flask_wtf import FlaskForm
from wtforms import FormField, StringField, SubmitField, EmailField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms.widgets import TextArea

#Login Form
class LoginForm(FlaskForm):
    user_name = StringField('Username', validators = [DataRequired(message = 'This field requires a value')])
    password = PasswordField('Password', validators = [DataRequired(message = 'This field requires a value')])
    submit = SubmitField('Login')

#Users Form
class UserForm(FlaskForm):
    name = StringField('Name', validators = [DataRequired(message = 'This field requires a value')])
    user_name = StringField('Username', validators = [DataRequired(message = 'This field requires a value')])
    email = EmailField('Email', validators = [DataRequired(message = 'This field requires a value'), 
                                Email(message = 'Please input a vaild email address!')])
    job_profile = StringField('Job Profile')
    password = PasswordField('Password', validators = [DataRequired(), EqualTo('password_confirm',
                                message = 'Passwords must match!')])
    password_confirm = PasswordField('Confirm Password')
    submit = SubmitField('Submit')

#Blog Post Form
class PostForm(FlaskForm):
    title = StringField('Title', validators = [DataRequired(message = 'This field requires a value')])
    content = StringField('Content', validators =  [DataRequired(message = 'This field requires a value')], 
        widget = TextArea())
    author = StringField('Author')
    slug = StringField('Slug', validators =  [DataRequired(message = 'This field requires a value')])
    submit = SubmitField('Submit')

#used intially, not needed anymore
class NameForm(FlaskForm):
    name = StringField("What's your name?", validators = [DataRequired(message = 'This field requires a value')])
    submit = SubmitField("Submit")

#used intially, not needed anymore
class PasswordForm(FlaskForm):
    email = EmailField('Email', validators = [DataRequired(message = 'This field requires a value')])
    password = PasswordField('Password', validators = [DataRequired()])
    submit = SubmitField('Submit')

