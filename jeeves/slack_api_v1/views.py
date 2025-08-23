from quart import request

from jeeves.outgoing.slack import send_message_to_slack
from . import slack_api_v1


@slack_api_v1.route("/send_message", methods=["POST"])
async def send_message_to_slack_route():
    """Receives a message to post on slack"""
    request_body = await request.get_json()
    send_message_to_slack(
        request_body["message"], request_body["channel"])
    return {"status": "OK"}, 200
