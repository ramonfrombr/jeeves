import pytest
from unittest.mock import patch, MagicMock
from unittest.mock import AsyncMock
from quart import Quart

# ---- App / client ----


@pytest.fixture
def app():
    app = Quart(__name__)
    from jeeves.slack_api_v1 import slack_api_v1  # adjust import as needed
    app.register_blueprint(slack_api_v1, url_prefix='/slack_api/v1')

    app.config["SLACK_TOKEN"] = "fake-token"
    app.config["SLACK_POST_URL"] = "https://slack.test/api/chat.postMessage"
    app.config["WEATHER_URL"] = "https://api.openweathermap.org/data/2.5/weather?q={text}&appid={token}"
    app.config["WEATHER_TOKEN"] = "fake-weather-token"
    return app


@pytest.fixture
def client(app):
    return app.test_client()


# ---- HTTP mocks ----
@pytest.fixture
def mock_requests_post():
    with patch("jeeves.outgoing.slack.send_message_to_slack", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = None  # or use AsyncMock() if you want to inspect further
        yield mock_post


@pytest.fixture
def mock_httpx_get():
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "main": {"temp": 293.15, "feels_like": 291.15}
        }
        # Important: make raise_for_status a normal mock, not async
        mock_response.raise_for_status = MagicMock(return_value=None)
        mock_get.return_value = mock_response
        yield mock_get

# ---- Data fixtures ----


@pytest.fixture
def slack_message_body_nested_text():
    return {
        "event": {
            "type": "message",
            "channel": "C123",
            "user": "U123",
            "text": "<@ABC> weather London",
            "ts": "123456.7890",
            "team": "T123",
            "blocks": [
                {
                    "type": "rich_text",
                    "block_id": "ABC",
                    "elements": [
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {"type": "user", "user_id": "ABC"},
                                {"type": "text", "text": " weather London"},
                            ],
                        }
                    ],
                }
            ],
        }
    }


@pytest.fixture
def slack_message_body_plain_text():
    return {
        "event": {
            "type": "message",
            "channel": "C123",
            "user": "U123",
            "text": "weather London",
            "ts": "123456.7890",
            "team": "T123",
        }
    }


@pytest.fixture
def slack_url_verification_body():
    return {"type": "url_verification", "challenge": "test-challenge-123"}


@pytest.fixture
def blog_comment_payload():
    return {
        "channel": "C_TEST",
        "message": "New Blog Comment",
        "post_title": "My Awesome Blog Post",
        "post_link": "https://example.com/blog/123",
        "comment_content": "This is a great article!",
        "comment_email": "test@example.com",
    }

# ---- Capture plain prints (stdout) ----


@pytest.fixture
def capture_print(capfd):
    """
    Use in tests that need to assert on print() output.
    Example:
        out = capture_print.read()
        assert "In process message" in out
    """
    class _Captured:
        def read(self):
            # Returns text printed since the last read/clear
            return capfd.readouterr().out

        def clear(self):
            # Drain buffers so the next read() only contains new output
            capfd.readouterr()
    return _Captured()


# ---- Capture logs from logging module ----
@pytest.fixture
def capture_logs(caplog):
    """
    Use when the code uses the logging module (INFO by default).
    Example:
        with capture_logs("jeeves", level="DEBUG"):
            ...
        assert any("Working on weather" in r.message for r in caplog.records)
    """
    from contextlib import contextmanager
    import logging

    @contextmanager
    def _ctx(logger_name="root", level="INFO"):
        lvl = getattr(logging, level.upper())
        caplog.set_level(
            lvl, logger=logger_name if logger_name != "root" else None)
        yield caplog  # caplog.records; caplog.text
    return _ctx
