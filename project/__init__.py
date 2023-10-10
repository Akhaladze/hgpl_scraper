import sys, os
sys.path.append(os.environ.get('APP_PATH'))
from flask import Flask, request, jsonify, config
from flask.cli import FlaskGroup


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.DevelopmentConfig")
    import models as models
    from models import db
    models.db.init_app(app)
    return app
