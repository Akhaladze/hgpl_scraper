# Description: Celery tasks 

# Constants: broker_url, redis_url, path TODO: move to config
broker_url = "pyamqp://scraper:scraper@192.168.65.80:5672/scraper_app"
#redis_url = "redis://192.168.65.130:6379/0"
redis_url = "redis://localhost:6379/0"
# 
import os, sys, requests, time, json, logging, datetime
# TODO: move to config
sys.path.append('/home/gnet/dev/scrapper_dev/project/')
sys.path.append('/home/gnet/dev/scrapper_dev/project/connectors/')

sys.path.append('~/data/')
sys.path.append('~/data/project/')
sys.path.append('~/data/project/connectors/')

#sys.path.append('~/data/project/connectors/tasks.py')


import redis, hashlib
from celery import Celery
from flask import current_app
from models import db, MainSDSstore

app = Celery('tasks',
            broker=broker_url,
            backend=redis_url,
            broker_use_ssl=False,
            result_backend_use_ssl=False)
app.conf.accept_content = ['pickle', 'json', 'msgpack', 'yaml']
app.conf.worker_send_task_events = True

path = str(os.getenv("APP_DOWNLOADS_PATH")) + '/sabic/'


@app.task
def add(x, y):
    return x + y


@app.task
def sleep(seconds):
    time.sleep(seconds)


@app.task
def echo(msg, timestamp=False):
    return "%s: %s" % (datetime.now(), msg) if timestamp else msg


@app.task
def error(msg):
    raise Exception(msg)

#db.init_app(app=current_app)

# Calculate filehash
@app.task(serializer='json')
def getFileHash(sdsPath:str, do_update:bool=False, do_commit:bool=False):
    '''Get filehash from SDS file and update hash in DB. Params: (dict) record, (str) sdsPath
         Return: True or False'''
    ## ?TODO: Size of file& MIME type?
    if os.path.isfile(sdsPath) and os.access(sdsPath, os.R_OK):
        with open(sdsPath,"rb") as f:
            bytes = f.read() # read entire file as bytes
            readable_hash = hashlib.sha256(bytes).hexdigest();
            print("Write hash to DB:", readable_hash)
            f.close()
            # Update hash in DB
            if do_update:
                filehash = str(readable_hash)
            else:
                print("FILE_NOT_FOUND")
    else:
        print("FILE_NOT_FOUND")
        filehash = str("FILE_NOT_FOUND")
    if do_commit:
        print("Write to DB: Hash", filehash)
        #db.session.commit()
    else:
        pass
    return '{"status": True, "readable_hash":' +  filehash + '}'

@app.task(serializer='json')
def downloadSds(id:int, filename:str, url:str, language:str, region:str, do_update:bool=False, do_commit:bool=False):
    # TODO: Add tasks to celery
    # TODO: Add logging
    print("Current Filename: ",  filename, "URL ",  url, "Status ",  status, "Language ",  language, "Region ",  region)
    headers = {'Accept-Encoding': 'gzip, deflate, br'
            ,'Sec-Ch-Ua': 'Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116'
            ,'Sec-Ch-Ua-Mobile': '?0'
            ,'Sec-Ch-Ua-Platform': "Linux"
            ,'Sec-Fetch-Dest': 'document'
            ,'Sec-Fetch-Mode': 'navigate'
            ,'Sec-Fetch-Site': 'none'
            ,'Sec-Fetch-User': '?1'
            ,'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
            ,'Accept': 'application/pdf'}

    if not None in (id, filename, url, language, region):
        try:
            response = requests.get(url, headers=headers)
            response_Query = response.content
            status_code = response.status_code
            print ("Current Status Code: ", status_code)
            if response_Query is not None and status_code == 200:
                # Save SDS File to Storage
                # Create new folder if not exists
                sdsPath = path + str(region) + "/" + str(language) + "/" + str(filename)
                if not os.path.exists(sdsPath):
                    os.makedirs(sdsPath)
                # Generate filename
                filename = sdsPath + str(filename)
                
                # Write SDS File to Storage
                with open(filename, 'wb') as f:
                    f.write(response_Query)
                    f.close()
                    # Update status in DB
                    status = 'done' 
            else:
                status = 'status_code: ' + str(status_code)
                status = status[1:20]
        except requests.exceptions.RequestException as e:
            print("Error: ", e)
            #continue
            pass
        finally:
            print("Write to DB: Status", status)
            db.session.commit()
            #time.sleep(1)
    return '{"filename":' +  filename + ', "url":' +  url + ', "status":' +  status + ', "language":' +  language + ', "region":' +  region + '}'

#if __name__ == "__main__":
#    app.start()
