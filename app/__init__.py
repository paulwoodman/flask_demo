import os

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, AnonymousUser
from flask.ext.openid import OpenID
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqlamodel import ModelView

from config import basedir, ADMINS

# Create Flask Object
app = Flask(__name__)

# Configure Flask Object from config file.
app.config.from_object('config')

# Get a SQLAlchemy DB object attached to the application.
db = SQLAlchemy(app)

# Initialize openID object
oid = OpenID(app, os.path.join(basedir, 'tmp'))

# Initialize Admin module
admin = Admin(app)

# Initialize Login Module

class Anonymous(AnonymousUser):
    name = u"Anonymous"

    def is_authenticated(user):
        return False

lm = LoginManager()
lm.anonymous_user = Anonymous
lm.init_app(app)
lm.login_view = 'login'


if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('technights.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('technights startup')


from app import views, models
from models import User, TechTalk
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(TechTalk, db.session))
