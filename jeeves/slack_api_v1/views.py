import requests
import logging
from quart import request, current_app
from jeeves.outgoing.slack import send_message_to_slack
from . import slack_api_v1


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@slack_api_v1.route("/message/send", methods=["POST"])
async def send_message_to_slack_route():
    """Receives a message to post on slack"""
    request_body = await request.get_json()
    send_message_to_slack(
        request_body["message"], request_body["channel"])
    return {"status": "OK"}, 200


def respond_to_slack_challenge(incoming_challenge):
    return incoming_challenge.get("challenge", ""), 200


def reply_message_to_slack(message, metadata):
    logger.debug(f"reply_message_to_slack {message}")
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['SLACK_TOKEN']}",
    }
    logger.debug(f"headers {headers}")
    logger.debug(metadata)
    response = requests.post(
        current_app.config["SLACK_POST_URL"],
        json={
            "token": current_app.config["SLACK_TOKEN"],
            "text": message,
            "channel": metadata["channel"]
        },
        headers=headers
    )
    response.raise_for_status()


def extract_slack_text(request_body):
    # Deep JSON structure
    elements = request_body["event"]["blocks"][0]["elements"][0]["elements"]
    for part in elements:
        if part["type"] == "text":
            return part["text"].lstrip()

    return request_body["event"]["text"].partition(">")[2].lstrip()


def outgoing_metadata(request_body):
    return {
        "type": "slack",
        "message_type": request_body["event"]["type"],
        "team": request_body["event"]["team"],
        "sender": request_body["event"]["user"],
        "channel": request_body["event"]["channel"],
        "ts": request_body["event"]["ts"],  # used for replies
    }


@slack_api_v1.route("/message/reply", methods=["POST"])
async def reply_message_to_slack_route():
    """Receive an event from Slack."""
    request_body = await request.get_json()

    # When setting up a Slack app, we are sent a verification
    # challenge, and we must respond with the token provided.
    if request_body.get("type", "") == "url_verification":
        logger.info("Responding to url verification challenge")
        return respond_to_slack_challenge(request_body)

    reply_message_to_slack(extract_slack_text(request_body),
                           outgoing_metadata(request_body))

    return {"status": "OK"}, 200
