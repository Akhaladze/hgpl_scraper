from flask import Flask, jsonify, config, current_app
from flask.cli import FlaskGroup, click
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB, ARRAY, UUID, TIMESTAMP
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, event
from sqlalchemy.exc import DatabaseError
import sys, requests, os

sys.path.append('/home/gnet/dev/hglp_scraper/project/connectors/')

path = str(os.getenv("APP_PATH")) + str("downloads/basf/")

import models as models
from models import db, BasfList

app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")
models.db.init_app(app)
app.app_context().push()
app.cli = FlaskGroup(app) # type: ignore

path = str(os.getenv("APP_PATH")) + str("downloads/basf/")
#@app.cli.command("get_status")
#@click.argument("record_id", default=1000)
#def get_status(record_id: int):
    #result = download_sds.delay(record_id)
    #result = add.delay(4,111)
    #print(result.ready())
    #print(result.get(timeout=1))
    #result.get(propagate=False)
    #print(result.get())   
    #return result.get()


@app.cli.command("get_data")
@click.argument("language", default='"en","bg","nl","da","et","fi","fr","de","el","hu","is","it","lv","lt","no","pl","pt","ro","ru","sh","sk","sl","es","sv","tr","uk","az","zh","zf","hr","cs","id","ja","kk","ko","ms","th","vi"')
@click.argument("region", default='"/reg_eu","/8a80814b7dbd2df2017de1199591644a","/c765f83b051cdb529fab5310da125286","/8a8081657eaf9592017f2b30c934674d","/8a80816f7530533f017598a4d16b36e8","/8a808154798e2b950179acfa3b731756","/un"')
@click.argument("lastpage", default=700)
def get_data(language, region, lastpage):
    '''Get data from BASF and save to DB. Params: (list) language[], (list) region[], (int) lastpage 
       Example: flask get_data --language ["en"] --region ["/reg_eu"]
       Default: flask get_data --language ["en","bg","nl","da","et","fi","fr","de","el","hu","is","it","lv","lt","no","pl","pt","ro","ru","sh","sk","sl","es","sv","tr","uk","az","zh","zf","hr","cs","id","ja","kk","ko","ms","th","vi"] --region ["/reg_eu","/8a80814b7dbd2df2017de1199591644a","/c765f83b051cdb529fab5310da125286","/8a8081657eaf9592017f2b30c934674d","/8a80816f7530533f017598a4d16b36e8","/8a808154798e2b950179acfa3b731756","/un"]
       Return: True '''
    page_counter = 0
    status_code = 200
    
    while status_code == 200 and page_counter < lastpage:
        url = 'https://products.basf.com/global/en/downloads/_jcr_content/root/responsivegrid/overview.results.json?facet:documentType[]=%2F8a8082d37dbd2df3017dc2b913a3076f&facet:contentLocation[]=%2Freg_eu&facet:contentLocation[]=%2F8a80814b7dbd2df2017de1199591644a&facet:contentLocation[]=%2Fc765f83b051cdb529fab5310da125286&facet:contentLocation[]=%2F8a8081657eaf9592017f2b30c934674d&facet:contentLocation[]=%2F8a80816f7530533f017598a4d16b36e8&facet:contentLocation[]=%2F8a808154798e2b950179acfa3b731756&facet:contentLocation[]=%2Fun&facet:contentLanguage[]=en&facet:contentLanguage[]=az&facet:contentLanguage[]=bg&facet:contentLanguage[]=zh&facet:contentLanguage[]=zf&facet:contentLanguage[]=hr&facet:contentLanguage[]=cs&facet:contentLanguage[]=da&facet:contentLanguage[]=nl&facet:contentLanguage[]=et&facet:contentLanguage[]=fi&facet:contentLanguage[]=fr&facet:contentLanguage[]=de&facet:contentLanguage[]=el&facet:contentLanguage[]=hu&facet:contentLanguage[]=is&facet:contentLanguage[]=id&facet:contentLanguage[]=it&facet:contentLanguage[]=ja&facet:contentLanguage[]=kk&facet:contentLanguage[]=ko&facet:contentLanguage[]=lv&facet:contentLanguage[]=lt&facet:contentLanguage[]=ms&facet:contentLanguage[]=no&facet:contentLanguage[]=pl&facet:contentLanguage[]=pt&facet:contentLanguage[]=ro&facet:contentLanguage[]=ru&facet:contentLanguage[]=sr&facet:contentLanguage[]=sh&facet:contentLanguage[]=sk&facet:contentLanguage[]=sl&facet:contentLanguage[]=es&facet:contentLanguage[]=sv&facet:contentLanguage[]=th&facet:contentLanguage[]=tr&facet:contentLanguage[]=uk&facet:contentLanguage[]=vi&page=' + str(page_counter)
        headers = {'Accept': 'application/json, text/plain'
                ,'Accept': 'application/json'
                ,'Accept-Encoding': 'gzip, deflate, br'
                ,'Accept-Language': 'ru-UA,ru;q=0.9,uk-UA;q=0.8,uk;q=0.7,ru-RU;q=0.6,en-US;q=0.5,en;q=0.4'
                #,'Cache-Control:': 'no-cache'
                ,'Sec-Ch-Ua': 'Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116'
                ,'Sec-Ch-Ua-Mobile': '?0'
                ,'Sec-Ch-Ua-Platform': "Linux"
                ,'Sec-Fetch-Dest': 'document'
                ,'Sec-Fetch-Mode': 'navigate'
                ,'Sec-Fetch-Site': 'none'
                ,'Sec-Fetch-User': '?1'
                ,'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
                ,'Accept': 'application/json'}
        data = {}
       # params = {'facet:documentType[]': '/8a8082d37dbd2df3017dc2b913a3076f'
       #         , 'facet:contentLocation[]': region
       #         , 'facet:contentLanguage[]': language
       #         , 'page': str(page_counter)}
        #/global/en/downloads/_jcr_content/root/responsivegrid/overview.results.json?facet:documentType[]=%2F8a8082d37dbd2df3017dc2b913a3076f&facet:contentLocation[]=%2Freg_eu&facet:contentLanguage[]=en&page=0
        response = requests.get(url
                                ,headers=headers
                                #,params=params
                                )
        # save response to db
        
        basf_sds_list = response.json()
        for item in basf_sds_list['results']:
            if item.get('variants') is None:
                continue
            item_variants = item['variants']
            for item_variant in item_variants:
                try:
                    db.session.add(BasfList(
                         url=item_variant['viewUrl']
                        ,filename=item_variant['fileName']
                        ,page=page_counter
                        ,language=item_variant['languages'][0]['id'].upper()
                        ,region=item_variant['legalAreas'][0]['id'].upper()
                        ,title=item['title']
                        ,product_id=item['id']
                        ,trade_productCode="not available"
                        ,url_pdf=item_variant['downloadUrl']
                        ,record_number="not available"
                        ,description="not available"
                        ,connector_id=1
                        ,status="new"
                        ,filesize=0
                        ,filehashes="not available"
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
    print("END Processing: BASF SDS List")
    return True


@app.cli.command("get_sds")
@click.argument("language", default="All")
@click.argument("region", default="All")
def get_sds(language, region):

    ''' Get SDS from Chemical Vendor, Params: (list) language, (list) region \n
        Example: flask get_sds --language "en" --region "/reg_eu" \n
        Default: flask get_sds --language "en" --region "/reg_eu" \n
        Return: SDS file '''
    status_code = 200
    while status_code == 200:
        # Get SDS File Data from DB
        #if language == "All" and region == "All":
        item = db.session.query(BasfList).filter(BasfList.status=="new").with_for_update(skip_locked=True).first() # type: ignore
        #elif language != "All" and region == "All":
        #    item = db.session.query(BasfList).filter(BasfList.status=="new").filter(BasfList.language==language).with_for_update(skip_locked=True).first() # type: ignore
        
        if item is None:
            break
        
            # TODO: Add tasks to celery
            # TODO: Add logging
        print("Current Item: ", item.filename, "URL ", item.url, "Page ", item.page, "Status ", item.status, "Language ", item.language, "Region ", item.region)
                
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
                path= str(os.getenv("APP_PATH")) + str("downloads/basf/")
                print ("Current Status Code: ", status_code)
                if response_Query is not None:
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
                item.status = 'error'
                continue
        except requests.exceptions.RequestException as e:
            print("Request Query: Get SDS error_code", e)
            item.status = 'error'
            # TODO: Add logging
            # TODO: Add allerting
            pass
            
        finally:
            print("Write to DB: BASF with Status", item.status)
            db.session.commit()
            #time.sleep(1)     
    print("END Processing: BASF SDS Download")
    # TODO: Add logging
    # TODO: END tasks to celery
    
    return True

if __name__ == "__main__":
    app.cli()
    