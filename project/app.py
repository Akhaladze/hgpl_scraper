
# Importing libraries
from flask import Flask, request, jsonify, config, current_app
from flask.cli import FlaskGroup, click
import time, sys, requests
# Models
from models import db, Connectors, MainSDSstore
# Not using now, but installed: bs4, html5lib, requests_html import HTMLSession

from __init__ import create_app

# INITIALIZATION
sys.path.append('~/dev/hgpl_scraper/project/')
app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")
db.init_app(app)
cli = FlaskGroup(app) # type: ignore

# Project management cli commands
@cli.command("create_db")
def create_db():
    try:
        app.flask_migrate.upgrade(app.config["SQLALCHEMY_DATABASE_URI"]) # type: ignore
    except:
        db.create_all()
        db.session.commit()
        db.session.close()      
    db.session.commit()

@cli.command("add_connector")
@click.argument("name", default="New Connector")
def seed_db(name:str):
    db.session.add(Connectors(name=name))
    MainSDSstore.addNewPartition(Connectors.query.filter_by(name=name)).orderby('asc').limit(1).id
    db.session.commit()
    db.session.close()
@cli.command("drop_db")
def drop_db():
    db.drop_all()
    db.session.commit()
    
if __name__ == "__main__":
    cli()