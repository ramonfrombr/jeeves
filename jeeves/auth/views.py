from quart import render_template, redirect, render_template, url_for
from .forms import LoginForm
from ..models import User
from . import auth
from .. import db
from quart_auth import current_user, login_required, login_user, logout_user, AuthUser


@auth.route("/login", methods=["GET", 'POST'])
def login():
    form = LoginForm()
    """
    if form.validate_on_submit():
        email, password = form.data["email"], form.data["password"]
        q = db.session.query(User).filter(User.email == email)
        user = q.first()
        if user is not None and user.verify_password(password):
            login_user(AuthUser(user.id))
            return redirect(url_for("index"))
    """
    return render_template("login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")
