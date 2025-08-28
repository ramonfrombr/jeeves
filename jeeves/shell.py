import asyncio
from jeeves import create_app


def create_app_for_shell(*args, **kwargs):
    """
    Run async factory inside an already running loop for Quart shell.
    """
    import nest_asyncio
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(create_app(*args, **kwargs))
