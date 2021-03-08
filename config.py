import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))


DEBUG = True


SQLALCHEMY_DATABASE_URI = 'postgresql://sondr@localhost:5432/fyyur'
SQLALCHEMY_TRACK_MODIFICATIONS = False