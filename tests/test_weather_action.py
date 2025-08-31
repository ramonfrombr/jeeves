import pytest
from jeeves.actions.weather import weather_action


@pytest.mark.asyncio
async def test_weather_action_returns_text(app, mock_httpx_get):
    async with app.app_context():
        result = await weather_action("weather London", {"user": "u1"})
        assert "temperature" in result
        assert "℃" in result
