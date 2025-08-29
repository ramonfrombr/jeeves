import asyncio
from quart import Blueprint, render_template
from jeeves.models import User
from ..db import Base, engine, get_session
from sqlalchemy.future import select
from quart_auth import current_user, login_required, login_user, logout_user, AuthUser


home = Blueprint("home", __name__)


@home.route("/")
@login_required
async def index():

    async for session in get_session():
        result = await session.execute(select(User).filter_by(email="ramonfrombr@gmail.com"))
        user = result.scalars().first()
    print(user.email)
    return await render_template("index.html")
