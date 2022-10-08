import audioop
from flask import Flask, render_template

#flask instance
app = Flask(__name__)

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