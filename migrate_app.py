import os
from flask import Flask
from jeeves import db  # shared db object
from flask_migrate import Migrate
import jeeves.models     # ensure models are loaded


def create_app():
    flask_app = Flask(__name__)
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL')
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(flask_app)
    Migrate(flask_app, db)

    return flask_app
