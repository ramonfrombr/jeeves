import quart_flask_patch
import wtforms as f
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = f.StringField("email", validators=[DataRequired()])
    password = f.PasswordField("password", validators=[DataRequired()])
    submit = f.SubmitField("Login")

    display = ["email", "password", "submit"]
