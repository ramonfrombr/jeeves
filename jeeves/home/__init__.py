import asyncio
from quart import Blueprint
from jeeves.models import User
from jeeves import db

home = Blueprint("home", __name__)


@home.route("/")
async def index():
    loop = asyncio.get_running_loop()

    # Run blocking DB query in a thread
    def get_user_sync():
        return db.session.query(User).filter(
            User.email == 'ramonfrombr@gmail.com').first()

    user = await loop.run_in_executor(None, get_user_sync)
    return "Hello" + user.email
