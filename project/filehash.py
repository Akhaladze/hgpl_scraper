from flask import Flask, jsonify, config, current_app
from flask.cli import FlaskGroup, click
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB, ARRAY, UUID, TIMESTAMP
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, event
from sqlalchemy.exc import DatabaseError
import sys, requests, os, json
from tasks import getFileHash
import models as models
from models import db, DowList, Connectors, MainSDSstore, BasfList
from celery import Celery, Task, current_task, states
from celery.exceptions import Ignore
from celery.result import AsyncResult
from time import sleep

app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")
models.db.init_app(app)
app.app_context().push()
app.cli = FlaskGroup(app) # type: ignore
path = str(app.config["PROJECT_PATH"]) + str("/downloads/sabic/")

#################################################################################################################
# Get params from user/script:
#################################################################################################################
# Chemical Product Name
# SDS Language (Optional)
# Region (Optional)
# SDS File (Optional)
# SDS File Hash (Optional)
# #################################################################################################################
# Get filepath(s) from DB
# Get DB record ID from DB
# #################################################################################################################
# Return: Filehash [SHA256]
# Filesizes (bytes)
# MIME type: [application/pdf]
# #################################################################################################################
# Error message: 
# status: 'done', 'updated' - that means that filehash was updated or created, 
# ['error'] - that means that filehash was not created/updated with following possible error messages:
# ['FILE_NOT_FOUND', 'FILE_NOT_ACCESSIBLE', 'MIME_TYPE_ERROR':-  Special worker (Queue) try fix it or redefine status
# #################################################################################################################

i=0

@app.cli.command("get_filehash")
@click.argument("language", default="All")
@click.argument("region", default="All")
@click.argument("filename", default="All")
@click.argument("connector_id", default="basf") # TODO: change to 'latest by date'
def get_filehash(language=None, region=None, filename=None, connector_id=None):
    result = None
    '''Get filehash from SDS file and save to DB. Params: (dict) record
        Return: True '''
    while True or result is not None and i > 10: # TODO: change to 'while True'
        # Get SDS File Data from DB
        record = db.session.query(MainSDSstore).filter(MainSDSstore.status == 'done').filter(MainSDSstore.connector_id == 4).with_for_update(skip_locked=True).first() # type: ignore
        #record = db.session.query(MainSDSstore).with_for_update(skip_locked=True).first() # type: ignore
        print("Record: ", record)
        if record is not None:
            try:        
                if not None in (record.id, record.filename, record.url, language, region):
                    print("TASK: GET_FILEHASH: Filename: ",record.filename,"Status: ",record.status,"Language: ", record.language, "Region: ", record.region)
                    #result=getFileHash.delay(record)
                    result=getFileHash.delay(10)
                    print(result.get())
                else:
                    continue
            except requests.exceptions.RequestException as e:
                print("Error_code", e)
                pass
            finally:
                #db.session.commit()
                print("Result: ", result)
                #time.sleep(1)
        else:
            print("No new records, exit")
            break   
    return True    

if __name__ == "__main__":
    app.cli()

if __name__ == "__main__":
    app.run()   
    
