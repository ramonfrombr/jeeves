import os
import logging
from quart import Quart
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

db = SQLAlchemy()


async def create_app(*args, **kwargs):
    app = Quart(__name__)

    app.config["SLACK_TOKEN"] = os.environ.get('SLACK_TOKEN')
    app.config["SLACK_POST_URL"] = os.environ.get('SLACK_POST_URL')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from .slack_api_v1 import slack_api_v1 as slack_api_v1_bp
    app.register_blueprint(slack_api_v1_bp)

    return app
