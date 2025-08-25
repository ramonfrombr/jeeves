import quart.flask_patch
from . import db
from werkzeug.security import check_password_hash, generate_password_hash


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(128))
    slack_id = db.Column(db.String(128))
    password = db.Column(db.String(128))
    location = db.Column(db.String(128))
    config = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self._authenticated = False

    def set_password(self, password):
        self.password = generate_password_hash(password)

    @property
    def is_authenticated(self):
        return self._authenticated

    def authenticate(self, password):
        checked = check_password_hash(self.password, password)
        self._authetnicated = checked
        return self._authenticated
