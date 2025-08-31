import pytest
from unittest.mock import patch, MagicMock
from unittest.mock import patch, AsyncMock


# ---- Tests ----
@pytest.mark.asyncio
async def test_send_message_to_slack_route(client, mocker):
    """
    Tests the /message/send route.
    Mocks the send_message_to_slack function to assert it's called correctly.
    """
    mock_send = mocker.patch("jeeves.slack_api_v1.views.send_message_to_slack")
    payload = {"message": "Hello, world!", "channel": "C123"}
    response = await client.post("/slack_api/v1/message/send", json=payload)
    data = await response.get_json()

    assert response.status_code == 200
    assert data == {"status": "OK"}
    mock_send.assert_called_once_with("Hello, world!", payload)


def test_respond_to_slack_challenge():
    """Tests the helper function that responds to Slack challenges."""
    from jeeves.slack_api_v1.views import respond_to_slack_challenge

    body = {"challenge": "test-challenge-123"}
    response, status = respond_to_slack_challenge(body)
    assert response == "test-challenge-123"
    assert status == 200


def test_extract_slack_text_nested_text(slack_message_body_nested_text):
    """Tests the text extraction from a complex Slack message body."""
    from jeeves.slack_api_v1.views import extract_slack_text

    text = extract_slack_text(slack_message_body_nested_text)
    assert text == "weather London"


def test_extract_slack_text_plain_text(slack_message_body_plain_text):
    """Tests the text extraction from a simple Slack message body."""
    from jeeves.slack_api_v1.views import extract_slack_text

    text = extract_slack_text(slack_message_body_plain_text)
    assert text == "weather London"


def test_outgoing_metadata(slack_message_body_plain_text):
    """Tests the creation of outgoing metadata from a Slack request."""
    from jeeves.slack_api_v1.views import outgoing_metadata

    metadata = outgoing_metadata(slack_message_body_plain_text)
    expected_metadata = {
        "type": "slack",
        "message_type": "message",
        "team": "T123",
        "sender": "U123",
        "channel": "C123",
        "ts": "123456.7890",
    }
    assert metadata == expected_metadata


@pytest.mark.asyncio
async def test_reply_message_to_slack_route_url_verification(client, slack_url_verification_body):
    """
    Tests the /message/reply route for a URL verification request.
    It should return the 'challenge' value from the request body.
    """
    response = await client.post("/slack_api/v1/message/reply", json=slack_url_verification_body)
    assert response.status_code == 200
    assert await response.get_data(as_text=True) == "test-challenge-123"


@pytest.mark.asyncio
async def test_reply_message_to_slack_route_normal_message(client, mocker, slack_message_body_plain_text):
    """
    Tests the /message/reply route for a normal message.
    It should call process_message with the correct text and metadata.
    """
    mock_process_message = mocker.patch(
        "jeeves.slack_api_v1.views.process_message")
    mocker.patch(
        "jeeves.slack_api_v1.views.extract_slack_text", return_value="weather London"
    )
    mocker.patch(
        "jeeves.slack_api_v1.views.outgoing_metadata", return_value={"mock": "metadata"}
    )

    response = await client.post("/slack_api/v1/message/reply", json=slack_message_body_plain_text)
    data = await response.get_json()

    assert response.status_code == 200
    assert data == {"status": "OK"}
    mock_process_message.assert_called_once_with(
        "weather London", {"mock": "metadata"})


def test_create_new_blog_comment_blocks(blog_comment_payload):
    """Tests the function that creates the Slack block payload for a new blog comment."""
    from jeeves.slack_api_v1.views import create_new_blog_comment_blocks
    blocks = create_new_blog_comment_blocks(blog_comment_payload)
    expected_blocks = [
        {"type": "header", "text": {"type": "plain_text",
                                    "text": "New Blog Comment", "emoji": True}},
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": "Post Title:\nMy Awesome Blog Post"},
                {"type": "mrkdwn", "text": "Post Link:\nhttps://example.com/blog/123"},
            ],
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": "Comment Content:\nThis is a great article!"},
                {"type": "mrkdwn", "text": "Comment Email:\ntest@example.com"},
            ],
        },
    ]
    assert blocks == expected_blocks


@pytest.mark.asyncio
async def test_send_message_to_slack_new_blog_comment(app, blog_comment_payload):
    with patch("jeeves.slack_api_v1.views.httpx.AsyncClient.post") as mock_post:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        from jeeves.slack_api_v1.views import send_message_to_slack_new_blog_comment

        async with app.app_context():
            await send_message_to_slack_new_blog_comment(blog_comment_payload)

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "https://slack.test/api/chat.postMessage"
        assert kwargs["json"]["channel"] == "C_TEST"
        assert "Authorization" in kwargs["headers"]


@pytest.mark.asyncio
async def test_send_message_to_slack_new_blog_comment_route(client, blog_comment_payload):
    """
    Tests the /message/send/new_blog_comment route.
    It asserts that the correct helper function is called.
    """
    with patch(
        "jeeves.slack_api_v1.views.send_message_to_slack_new_blog_comment",
        new_callable=AsyncMock,
    ) as mock_send:
        response = await client.post(
            "/slack_api/v1/message/send/new_blog_comment", json=blog_comment_payload
        )
        data = await response.get_json()

        assert response.status_code == 200
        assert data == {"status": "OK"}
        mock_send.assert_awaited_once_with(blog_comment_payload)
