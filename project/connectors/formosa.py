from flask import Flask, jsonify, config, current_app
from flask.cli import FlaskGroup, click
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB, ARRAY, UUID, TIMESTAMP
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, event
from sqlalchemy.exc import DatabaseError
import sys, requests, os, bs4, lxml

from tasks import downloadSds

import models as models
from models import db, MainSDSstore

app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")
models.db.init_app(app)
app.app_context().push()
app.cli = FlaskGroup(app) # type: ignore

path = str(app.config["PROJECT_PATH"]) + str("/downloads/formosa/")

@app.cli.command("get_data")
@click.argument("language", default='All')
def get_data(language):
    '''Get data from FORMOSA and save to DB. Params: (list) language[]
       Return: True '''
    
    status_code = 200
    
    url = 'https://www.fpcusa.com/support/safety-data-sheets/#1635867027163-ba4afe43-7030'
    
    payload = {}
    headers = {
    'Accept': 'application/html',
    'Accept-Encoding': 'gzip, deflate, br',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"'
    }

    response = requests.request("GET", url, headers=headers)
    # save response to db
    #print(response.text.encode('utf8'))
    if response.text is not None:
        sds_list = response.text
        soup = bs4.BeautifulSoup(sds_list, 'lxml')
        product1 = soup.findAll('div', id='1623339222686-fc97853b-a15d',  limit=100, recursive=True)
        product2 = soup.findAll('div', id='1635866797781-837bb285-2651',  limit=100, recursive=True)
        product3 = soup.findAll('div', id='1635867027163-ba4afe43-7030',  limit=100, recursive=True)
        product4 = soup.findAll('div', id='1635867147697-de53c7c1-cc17',  limit=100, recursive=True)
        product5 = soup.findAll('div', id='1635867255610-20757380-5685',  limit=100, recursive=True)
        
       
        for product in (product1, product2, product3, product4, product5):
            for item in product:
                for item in item.findAll('a', href=lambda x: x and x.endswith('.pdf')):
                    print(item['href'])
                    print(item['href'].split('/')[-1])
                    print(item.text)
                    
                    url="https://www.fpcusa.com" + item['href']
                    filename=item['href'].split('/')[-1]
                    language = filename.split('-')[-1]
                    language = language[-6:-4]
                    region = filename.split('-')[-2]

                    try:
                        db.session.add(MainSDSstore(
                            url=url
                            ,filename=filename
                            ,language=language.upper()
                            ,region=region.upper()
                            ,country=region.upper()
                            ,title='FORMOSA SDS'
                            ,product_id='FORMOSA SDS'
                            ,description='FORMOSA SDS'
                            ,connector_id=6
                            ,status="new"
                            ,filesize=0
                            ,filehashes="not available"
                            ,conectors_metadata='{}'
                            ,version='1'
                            )) # type: ignore
                        db.session.commit()
                    except DatabaseError as e:
                        db.session.rollback()
                        #time.sleep(1)
                        # TODO: Add logging
                        # TODO: Add allerting
                        print ("Error: ", e)
                        continue
                    finally:
                        #time.sleep(1)
                        db.session.close()
                        pass
        status_code = response.status_code    
        print ("Status code ", status_code)
    print("END Processing: FORMOSA SDS List")
    return True


@app.cli.command("get_sds")
@click.argument("language", default="All")
@click.argument("region", default="All")
def get_sds(language, region):

    ''' Get SDS from FORMOZA Chemical Vendor, Params: (list) language, (list) region \n
        Return: SDS file '''
    while True:
        # Get SDS File Data from DB
        item = db.session.query(MainSDSstore).filter(MainSDSstore.status == 'new').filter(MainSDSstore.connector_id == 6).with_for_update(skip_locked=True).first() # type: ignore
        if item is None:
            break
        # TODO: Add tasks to celery
        # TODO: Add logging

        print("Current Item: ", item.filename, "URL ", item.url, "Status ", item.status, "Language ", item.language, "Region ", item.region)
                
        id = item.id
        filename = item.filename
        url = item.url
        language = item.language
        region = item.region
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
        try:
            if not None in (id, filename, url, language, region):
                response = requests.get(url, headers=headers)
                response_Query = response.content
                status_code = response.status_code
                print ("Current Status Code: ", status_code)
                if response_Query is not None and status_code == 200:
                    # Save SDS File to Storage
                    
                    # Create new folder if not exists
                    sdsPath = path + str(region) + "/" + str(language) + "/"
                    if not os.path.exists(sdsPath):
                        os.makedirs(sdsPath)
                    
                    # Generate filename
                    filename = sdsPath + str(filename)
                    
                    # Write SDS File to Storage
                    with open(filename, 'wb') as f:
                        f.write(response_Query)
                        f.close()
                    
                    # Update status in DB
                    item.status = 'done'  
            else:
                continue
        except requests.exceptions.RequestException as e:
            print("Request Query: Get SDS error_code", e)
            item.status = 'status_code: ' + str(status_code)
            item.status = item.status[1:20]
            # TODO: Add logging
            # TODO: Add allerting
            pass
            
        finally:
            print("Write to DB: FORMOZA with Status", item.status)
            db.session.commit()
            #time.sleep(1)     
    print("END Processing: FORMOZA SDS Download")
    # TODO: Add logging
    # TODO: END tasks to celery
    return True

if __name__ == "__main__":
    app.cli()
    