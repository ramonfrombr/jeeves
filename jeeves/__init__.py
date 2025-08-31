# Put the import here when running the app

import os
import asyncio
import logging

from quart import Quart, redirect, render_template, url_for
from quart_auth import QuartAuth, Unauthorized, login_required


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


auth_manager = QuartAuth()


async def create_app(*args, **kwargs):

    # Put the import here when running migrations
    # import quart_flask_patch

    app = Quart(__name__)
    app.config["SECRET_KEY"] = "secret"
    app.config["SLACK_TOKEN"] = os.environ.get('SLACK_TOKEN')
    app.config["SLACK_POST_URL"] = os.environ.get('SLACK_POST_URL')
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL')
    app.config["WEATHER_URL"] = os.environ.get('WEATHER_URL')
    app.config["WEATHER_TOKEN"] = os.environ.get('WEATHER_TOKEN')

    auth_manager.init_app(app)

    @app.errorhandler(Unauthorized)
    async def redirect_to_login(*_):
        return redirect(url_for("auth.login"))

    from .slack_api_v1 import slack_api_v1 as slack_api_v1_bp
    app.register_blueprint(slack_api_v1_bp, url_prefix='/slack_api/v1')

    from .auth import auth as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .home import home as home_bp
    app.register_blueprint(home_bp, url_prefix="/")

    return app

app = None


# Remove these lines when running the shell
loop = asyncio.get_event_loop()
app = loop.run_until_complete(create_app())
