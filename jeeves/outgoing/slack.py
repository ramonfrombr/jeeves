import requests
from quart import current_app


def send_message_to_slack(message, channel):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['SLACK_TOKEN']}",
    }
    response = requests.post(
        current_app.config["SLACK_POST_URL"],
        json={
            "token": current_app.config["SLACK_TOKEN"],
            "text": message,
            "channel": channel
        },
        headers=headers
    )
    response.raise_for_status()
