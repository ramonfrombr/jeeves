import pytest
from jeeves.controller.message_router import process_message
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_process_message_prints_and_sends(app, capture_print, mock_httpx_get):
    with patch("jeeves.outgoing.slack.httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock(return_value=None)
        mock_post.return_value = mock_response

        async with app.app_context():
            capture_print.clear()
            await process_message("weather London", {"channel": "C123"})

        printed = capture_print.read()
        assert "In process message with 'weather London'" in printed
        assert "Working on weather" in printed

        mock_post.assert_called_once()
        assert mock_post.call_args.kwargs["json"]["channel"] == "C123"


"""
--- Optional (future): if you switch print() → logging
---

import logging
import pytest
from jeeves.controller.message_router import process_message

# Example: if you change prints to logging.getLogger("jeeves.router").info(...)
@pytest.mark.asyncio
async def test_process_message_logs(app, mock_requests_get, mock_requests_post, capture_logs):
    async with app.app_context():
        with capture_logs("jeeves.router", level="DEBUG") as logs:
            await process_message("weather London", {"channel": "C123"})

    assert any("In process message" in r.message for r in logs.records)
    assert any("Working on weather" in r.message for r in logs.records)
"""
