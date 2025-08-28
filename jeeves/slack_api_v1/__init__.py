from quart import Blueprint

slack_api_v1 = Blueprint("slack_api_v1", __name__)

from . import views
