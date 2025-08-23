import os
import asyncio
import logging
from quart import Quart

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def create_app(name=__name__):
    app = Quart(name)
    app.config["SLACK_TOKEN"] = os.environ.get('SLACK_TOKEN')
    app.config["SLACK_POST_URL"] = os.environ.get('SLACK_POST_URL')

    from .slack_api_v1 import slack_api_v1 as slack_api_v1_bp
    app.register_blueprint(slack_api_v1_bp)

    return app

app = None

loop = asyncio.get_event_loop()
app = loop.run_until_complete(create_app())
