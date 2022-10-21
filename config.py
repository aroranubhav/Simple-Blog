from distutils.debug import DEBUG
import os

SECRET_KEY = os.urandom(32)
base_dir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://maxi:AlMax579@localhost:5432/users' 
SQLALCHEMY_TRACK_MODIFICATIONS = False