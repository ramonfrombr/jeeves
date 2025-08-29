import wtforms as f
from quart_wtf import QuartForm
from wtforms.validators import DataRequired


class LoginForm(QuartForm):
    email = f.StringField("email", validators=[DataRequired()])
    password = f.PasswordField("password", validators=[DataRequired()])
    submit = f.SubmitField("Login")

    display = ["email", "password", "submit"]
