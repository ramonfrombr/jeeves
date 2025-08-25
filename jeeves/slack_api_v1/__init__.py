from quart import Blueprint

slack_api_v1 = Blueprint("slack_api_v1", __name__, url_prefix='/slack_api/v1')

from . import views