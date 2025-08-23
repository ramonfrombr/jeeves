import os
import asyncio
import logging
import requests
from quart import Quart, request

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def create_app(name=__name__):
    app = Quart(name)
    app.config["SLACK_TOKEN"] = os.environ.get('SLACK_TOKEN')
    app.config["SLACK_POST_URL"] = os.environ.get('SLACK_POST_URL')

    from .slack_api_v1 import slack_api_v1 as slack_api_v1_bp
    app.register_blueprint(slack_api_v1_bp)

    def respond_to_slack_challenge(incoming_challenge):
        return incoming_challenge.get("challenge", ""), 200

    def post_to_slack(message, metadata):
        print(f"post_to_slack {message}")
        headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {app.config['SLACK_TOKEN']}",
        }
        print(f"headers {headers}")
        print(metadata)
        response = requests.post(
            app.config["SLACK_POST_URL"],
            json={
                "token": app.config["SLACK_TOKEN"],
                "text": message,
                "channel": metadata["channel"]
            },
            headers=headers
        )
        response.raise_for_status()

    def post_to_slack_new_comment_blog(message, channel, title, link, email, comment):
        headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {app.config['SLACK_TOKEN']}",
        }
        response = requests.post(
            app.config["SLACK_POST_URL"],
            json={
                "token": app.config["SLACK_TOKEN"],
                "channel": channel,
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": message,
                            "emoji": True
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"Post Title:\n{title}"
                            },
                        ]
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"Post Link:\n{link}"
                            },
                        ]
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"Comment Email:\n{email}"
                            },
                        ]
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"Comment Content:\n{comment}"
                            },
                        ]
                    },
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

    @app.route("/api/slack/new-comment-blog", methods=["POST"])
    async def new_comment_blog():
        request_body = await request.get_json()
        post_to_slack_new_comment_blog(
            request_body["message"],
            request_body["channel"],
            request_body["post_title"],
            request_body["post_link"],
            request_body["comment_email"],
            request_body["comment_content"]
        )
        return {"status": "OK"}, 200

    return app

app = None

loop = asyncio.get_event_loop()
app = loop.run_until_complete(create_app())
