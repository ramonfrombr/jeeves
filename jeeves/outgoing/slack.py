import httpx
from quart import current_app


async def send_message_to_slack(message, metadata):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['SLACK_TOKEN']}",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            current_app.config["SLACK_POST_URL"],
            json={
                "token": current_app.config["SLACK_TOKEN"],
                "text": message,
                "channel": metadata["channel"]
            },
            headers=headers
        )
        response.raise_for_status()
