import httpx
import logging
from quart import request, current_app
from jeeves.controller.message_router import process_message
from jeeves.outgoing.slack import send_message_to_slack
from . import slack_api_v1


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@slack_api_v1.route("/message/send", methods=["POST"])
async def send_message_to_slack_route():
    """Receives a message to post on slack"""
    request_body = await request.get_json()
    await send_message_to_slack(
        request_body["message"], request_body)
    return {"status": "OK"}, 200


def respond_to_slack_challenge(incoming_challenge):
    return incoming_challenge.get("challenge", ""), 200


def extract_slack_text(request_body):
    event = request_body.get("event", {})
    blocks = event.get("blocks")

    if blocks:
        try:
            elements = blocks[0]["elements"][0]["elements"]
            extracted_text = "".join(e.get("text", "")
                                     for e in elements if e["type"] == "text").strip()
            return extracted_text
        except (KeyError, IndexError, TypeError):
            pass  # fall back to plain text

    return event.get("text", "").strip()


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

    await process_message(extract_slack_text(request_body),
                          outgoing_metadata(request_body))

    return {"status": "OK"}, 200


def create_new_blog_comment_blocks(request_body):
    return [
        {
            "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": request_body["message"],
                        "emoji": True
                    }
        },
        {
            "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"Post Title:\n{request_body['post_title']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"Post Link:\n{request_body['post_link']}"
                        },
                    ]
        },
        {
            "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"Comment Content:\n{request_body['comment_content']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"Comment Email:\n{request_body['comment_email']}"
                        },
                    ]
        },
    ]


async def send_message_to_slack_new_blog_comment(request_body):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['SLACK_TOKEN']}",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            current_app.config["SLACK_POST_URL"],
            json={
                "token": current_app.config["SLACK_TOKEN"],
                "channel": request_body["channel"],
                "blocks": create_new_blog_comment_blocks(request_body),
            },
            headers=headers
        )
        response.raise_for_status()


@slack_api_v1.route("/message/send/new_blog_comment", methods=["POST"])
async def send_message_to_slack_new_blog_comment_route():
    request_body = await request.get_json()
    await send_message_to_slack_new_blog_comment(request_body)
    return {"status": "OK"}, 200
