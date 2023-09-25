from flask import Flask, jsonify, config, current_app
from flask.cli import FlaskGroup, click
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB, ARRAY, UUID, TIMESTAMP
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, event
from sqlalchemy.exc import DatabaseError
import sys, requests, os
#from project.connectors.tasks import download_sds, add
from project.connectors.tasks import download_sds
#sys.path.append('/home/gnet/dev/scrapper_dev/project/')
#path = str(os.getenv("APP_PATH")) + str("downloads/sabic/")

import models as models
from models import db, DowList, Connectors, MainSDSstore, BasfList

app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")
models.db.init_app(app)
app.app_context().push()
app.cli = FlaskGroup(app) # type: ignore

path = str(app.config["PROJECT_PATH"]) + str("/downloads/sabic/")

material_number_list_start = 220000
material_number_list_end = 220999
                           

@app.cli.command("get_data")
@click.argument("language", default='All')
@click.argument("region", default='All')
def get_data(language, region):
    '''Get data from SABIC and save to DB. Params: (list) language[], (list) region[]
       Return: True '''
    page_counter = material_number_list_start
    status_code = 200
    

    while status_code == 200 and page_counter < material_number_list_end:
        #url = 'https://zehsonesdsext-tjd0i1flxa.dispatcher.sa1.hana.ondemand.com/v1/SDS/DocHeaderSet?spnego=disabled&$skip=0&$top=100&$orderby=Maktx%20asc,Matnr%20asc,Subid%20asc&$filter=substringof(%27' + str(page_counter) + '27,Matnr)%20and%20Laiso%20eq%20%27EN%27%20and%20(Reptype%20eq%20%27MSDS%27%20or%20Reptype%20eq%20%27SDS%27)&$inlinecount=allpages'
        url = 'https://zehsonesdsext-tjd0i1flxa.dispatcher.sa1.hana.ondemand.com/v1/SDS/DocHeaderSet?spnego=disabled&$skip=0&$top=100&$orderby=Maktx%20asc,Matnr%20asc,Subid%20asc&$filter=substringof(%27' + str(page_counter) + '%27,Matnr)%20and%20(Reptype%20eq%20%27MSDS%27%20or%20Reptype%20eq%20%27SDS%27)&$inlinecount=allpages'


        payload = {}
        headers = {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru-UA',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': 'SL_G_WPT_TO=en; SL_GWPT_Show_Hide_tmp=1; SL_wptGlobTipTmp=1; BIGipServerdispatcher.sa1.hana.ondemand.com=!oVHnyGH/3NmhRi3LaQg4rmbrgSZfP8ICR47QIAkhb1q+5D6ItYL/BVd4UbF/0Vhgbgnmqgyr1tkOnQ==; JSESSIONID=CEAD9449393932F7DF38A2C0A21229B1939FAAB5FC25F70F582BD2638BA498D0',
        'DataServiceVersion': '2.0',
        'Host': 'zehsonesdsext-tjd0i1flxa.dispatcher.sa1.hana.ondemand.com',
        'MaxDataServiceVersion': '2.0',
        'Pragma': 'no-cache',
        'Referer': 'https://zehsonesdsext-tjd0i1flxa.dispatcher.sa1.hana.ondemand.com/index.html',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sap-cancel-on-close': 'true',
        'sap-contextid-accept': 'header',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        # save response to db
        #print(response.text.encode('utf8'))
        if response.json().get('d') is None:
            page_counter += 1
            continue
        sds_list = response.json()['d']
        pcounter = sds_list['__count']
        for item in sds_list['results']:
            if item.get('__metadata') is None:
                continue
            sabic_url = "https://zehsonesdsext-tjd0i1flxa.dispatcher.sa1.hana.ondemand.com/v1/SDS//DocContentSet(Matnr='" + str(item['Matnr']) + "',Subid='" + str(item['Subid']) + "',Sbgvid='" + str(item['Sbgvid']) + "',Laiso='" + str(item['Laiso']) + "',Vkorg='')/DocContentData/$value"
            #https://zehsonesdsext-tjd0i1flxa.dispatcher.sa1.hana.ondemand.com/v1/SDS//DocContentSet(Matnr='22057344',Subid='630000006447',Sbgvid='SDS_NL',Laiso='EN',Vkorg='')/DocContentData/$value
            try:
                db.session.add(MainSDSstore(
                    url=sabic_url
                    ,filename=item['Matnr'] + "_" + item['Subid'] + "_" + item['Sbgvid'] + "_" + item['Laiso'] + "_" + item['Vkorg'] + ".pdf"
                    ,language=item['Laiso'].upper()
                    ,region=item['Rvlid'].upper()
                    ,country=item['Rvlid'].upper()
                    ,title=item['Maktx']
                    ,product_id=item['Matnr']
                    ,description=item['Ldepnam']
                    ,connector_id=4
                    ,status="new"
                    ,filesize=0
                    ,filehashes="not available"
                    ,conectors_metadata=item
                    ,version=item['Version']
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
        page_counter += 1
        status_code = response.status_code
        print ("Current Page: ", page_counter)
        print ("Stattus code ", status_code)
        #print ("Response: ", response.content)
        #time.sleep(3)
    print("END Processing: SABIC SDS List")
    return True


@app.cli.command("get_sds")
@click.argument("language", default="EN")
@click.argument("region", default="All")
def get_sds(language, region):

    ''' Get SDS from SABIC Chemical Vendor, Params: (list) language, (list) region \n
        Example: flask get_sds --language "en" --region "/reg_eu" \n
        Default: flask get_sds --language "en" --region "All" \n
        Return: SDS file '''
    while True:
        # Get SDS File Data from DB
        item = db.session.query(MainSDSstore).filter(MainSDSstore.status == 'new').filter(MainSDSstore.connector_id == 4).with_for_update(skip_locked=True).first() # type: ignore
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
            print("Write to DB: SABIC with Status", item.status)
            db.session.commit()
            #time.sleep(1)     
    print("END Processing: SABIC SDS Download")
    # TODO: Add logging
    # TODO: END tasks to celery
    return True

#if __name__ == "__main__":
    #app.cli()
if __name__ == "__main__":
    app.cli()
    