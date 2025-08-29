from quart import render_template, redirect, render_template, url_for
from .forms import LoginForm
from ..models import User
from . import auth
from quart_auth import current_user, login_required, login_user, logout_user, AuthUser
from ..db import Base, engine, get_session
from sqlalchemy.future import select


@auth.route("/login", methods=["GET", 'POST'])
async def login():
    form = await LoginForm().create_form()
    if await form.validate_on_submit():
        email, password = form.data["email"], form.data["password"]

        user = None
        async for session in get_session():
            result = await session.execute(select(User).filter_by(email=email))
            user = result.scalars().first()

        if user and user.verify_password(password):
            login_user(AuthUser(user.id))
            return redirect(url_for("home.index"))
    return await render_template("login.html", form=form)


@auth.route("/logout")
@login_required
async def logout():
    logout_user()
    return redirect("/")
