import asyncio
from quart import Quart


async def create_app(name=__name__):
    app = Quart(name)
    return app

app = None

loop = asyncio.get_event_loop()
app = loop.run_until_complete(create_app())
