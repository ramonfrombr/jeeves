import os
import requests
import asyncio
import logging
from quart import Quart, request, current_app

app = Quart(__name__)
app.config["SLACK_TOKEN"] = os.environ.get('SLACK_TOKEN')
app.config["SLACK_POST_URL"] = os.environ.get('SLACK_POST_URL')


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def respond_to_slack_challenge(incoming_challenge):
    return incoming_challenge.get("challenge", ""), 200


def post_to_slack(message, metadata):
    print(f"post_to_slack {message}")
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['SLACK_TOKEN']}",
    }
    print(f"headers {headers}")
    print(metadata)
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


def post_to_slack_external(message, channel):
    print(f"post_to_slack_external {message}")
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['SLACK_TOKEN']}",
    }
    print(f"headers {headers}")
    print(f"channel {channel}")
    response = requests.post(
        current_app.config["SLACK_POST_URL"],
        json={
            "token": current_app.config["SLACK_TOKEN"],
            "text": message,
            "channel": channel,
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "New request",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*Type:*\nPaid Time Off"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*Created by:*\n<example.com|Fred Enriquez>"
                        }
                    ]
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*When:*\nAug 10 - Aug 13"
                        }
                    ]
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "emoji": True,
                                "text": "Approve"
                            },
                            "style": "primary",
                            "value": "click_me_123"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "emoji": True,
                                "text": "Reject"
                            },
                            "style": "danger",
                            "value": "click_me_123"
                        }
                    ]
                }
            ]
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


@app.route("/api/slack", methods=["POST"])
async def incoming_slack_endpoint():
    """Receive an event from Slack."""
    request_body = await request.get_json()

    # When setting up a Slack app, we are sent a verification
    # challenge, and we must respond with the token provided.
    if request_body.get("type", "") == "url_verification":
        logger.info("Responding to url verification challenge")
        return respond_to_slack_challenge(request_body)

    post_to_slack(extract_slack_text(request_body),
                  outgoing_metadata(request_body))

    return {"status": "OK"}, 200


@app.route("/api/slack/external", methods=["POST"])
async def external_slack_message():
    """Receives a message to post on slack from external app"""
    request_body = await request.get_json()
    post_to_slack_external(request_body["message"], request_body["channel"])
    return {"status": "OK"}, 200

if __name__ == "__main__":
    app.run()
