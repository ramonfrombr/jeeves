import asyncio
import logging
from quart import Quart, request

app = Quart(__name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def respond_to_slack_challenge(incoming_challenge):
    return incoming_challenge.get("challenge", ""), 200


@app.route("/api/slack", methods=["POST"])
async def incoming_slack_endpoint():
    """Receive an event from Slack."""
    request_body = await request.get_json()

    # When setting up a Slack app, we are sent a verification
    # challenge, and we must respond with the token provided.
    if request_body.get("type", "") == "url_verification":
        logger.info("Responding to url verification challenge")
        return respond_to_slack_challenge(request_body)

if __name__ == "__main__":
    app.run()
