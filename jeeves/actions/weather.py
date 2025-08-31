import httpx
from quart import current_app
from urllib.parse import quote as urlquote


def kelvin_to_celcius(kelvin):
    return int(kelvin - 273.15)


async def process_weather_response(weather_data):
    temperature = kelvin_to_celcius(weather_data["main"]["temp"])
    feels_like = kelvin_to_celcius(weather_data["main"]["feels_like"])
    return f"The temperature is {temperature}℃ and it feels like {feels_like}℃"


async def fetch_weather(location):
    text = urlquote(location)

    url = current_app.config["WEATHER_URL"].format(
        text=text, token=current_app.config["WEATHER_TOKEN"]
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code == 404:
        return f"Sorry, I couldn't find weather for '{location}'."

    response.raise_for_status()
    json_data = response.json()
    return await process_weather_response(json_data)


async def weather_action(text, metadata):
    # Turn the text into something that's probably a location
    # Allow:
    # weather in location
    # weather location
    if not text:
        # TODO look up user.
        location = "London, UK"
    else:
        location = text.replace("weather", "").replace("in", "").strip()

    return await fetch_weather(location)
