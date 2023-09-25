from flask import Flask, request, jsonify, config, current_app
from flask.cli import FlaskGroup
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB, ARRAY, UUID, TIMESTAMP
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
import sys, requests, time, json, os

sys.path.append('~/dev/hgpl_scraper/project/')
import models as models
from models import db, DowList, Connectors, MainSDSstore, BasfList

app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")
models.db.init_app(app)
app.app_context().push()
cli = FlaskGroup(app) # type: ignore
# Path: project/dow.py
path = '~/dev/hgpl_scraper/project/downloads/dow/'
session = requests.Session()

proxies = {
   'http': 'http://146.0.80.152:8080',
   'http': 'http://146.0.80.189:8080'
}


###############################################################################################################################
# API Call's for Dow
###############################################################################################################################
# Query1: Get Dow List
authorization1 = 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJmaWx0ZXIiOiIoQHNvdXJjZT1Eb3cuY29tIE9SIEBzb3VyY2U9UHJvZHVjdCBPUiBAc291cmNlPT1cIkRvY3VtZW50cyAtIFhNTCAtIFB1c2hcIikgQGRvd19iYXNlcm9sZT0ocHVibGljKSBAZG93X2N1c3RvbWVydHlwZT0ocHVibGljKSBAZG93X3NlbGxhYmxlY291bnRyeT0oVUEscHVibGljKSBAZG93X2hpZXJhcmNoeT0ocHVibGljKSAoTk9UIEBkb3dfc2VhcmNoYWxsb3dlZCBPUiBAZG93X3NlYXJjaGFsbG93ZWQ9KHllcyx0cnVlKSkgQGRvd19sb2NhbGU9PWVuX3VzIiwic2VhcmNoSHViIjoiRG93Q29tTWFpblNlYXJjaCIsInY4Ijp0cnVlLCJ0b2tlbklkIjoic2xudnFubW00cmc2cnJ6enc1cXNwaWtrY2EiLCJvcmdhbml6YXRpb24iOiJ0aGVkb3djaGVtaWNhbGNvbXBhbnlwcm9kdWN0aW9uZHpmdGFsODkiLCJ1c2VySWRzIjpbeyJ0eXBlIjoiVXNlciIsIm5hbWUiOiItMzk1NDA5MTQ1IiwicHJvdmlkZXIiOiJFbWFpbCBTZWN1cml0eSBQcm92aWRlciJ9XSwicm9sZXMiOlsicXVlcnlFeGVjdXRvciJdLCJpc3MiOiJTZWFyY2hBcGkiLCJleHAiOjE2OTM5MDA4NzgsImlhdCI6MTY5MzgxNDQ3OH0.tgl9XONAsB_T2D-WPide97HaSgsyAV8kwBQwHO7sMJY' 
def query1(numberOfResults, excerptLength, locale,q, firstResult):
    organizationId = {"organizationId": "thedowchemicalcompanyproductiondzftal89"}
    url_q1 = "https://platform.cloud.coveo.com/rest/search/v2?" + str(organizationId)
    payload_q1 = {
         'actionsHistory':[]
        ,'referrer': ''
        ,'isGuestUser': False
        ,'q': q
        ,'searchHub': 'DowComSDSFinder'
        ,'locale': locale
        ,'firstResult': firstResult
        ,'numberOfResults': numberOfResults
        ,'firstResult': firstResult
        ,'excerptLength': excerptLength
        ,'filterField': '@foldingcollection'
        ,'filterFieldRange': 2
        ,'parentField': '@foldingchild'
        ,'childField': '@foldingparent'
        ,'enableDidYouMean': True
        ,'sortCriteria': 'relevancy'
        ,'queryFunctions': []
        ,'rankingFunctions': []
        ,'facetOptions': {}
        ,'categoryFacets': []
        ,'retrieveFirstSentences': True
        ,'timezone': 'Europe/Berlin'
        ,'enableQuerySyntax': False
        ,'enableDuplicateFiltering': False
        ,'enableCollaborativeRating': False
        ,'debug': False
        ,'allowQueriesWithoutKeywords': False 
    }
    headers_q1 = {
    'accept': '*/*',
    'accept-language': 'en-DE,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
    'authority': 'platform.cloud.coveo.com',
    'authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJmaWx0ZXIiOiIoQHNvdXJjZT1Eb3cuY29tIE9SIEBzb3VyY2U9UHJvZHVjdCBPUiBAc291cmNlPT1cIkRvY3VtZW50cyAtIFhNTCAtIFB1c2hcIikgQGRvd19iYXNlcm9sZT0ocHVibGljKSBAZG93X2N1c3RvbWVydHlwZT0ocHVibGljKSBAZG93X3NlbGxhYmxlY291bnRyeT0oVUEscHVibGljKSBAZG93X2hpZXJhcmNoeT0ocHVibGljKSAoTk9UIEBkb3dfc2VhcmNoYWxsb3dlZCBPUiBAZG93X3NlYXJjaGFsbG93ZWQ9KHllcyx0cnVlKSkgQGRvd19sb2NhbGU9PWVuX3VzIiwic2VhcmNoSHViIjoiRG93Q29tTWFpblNlYXJjaCIsInY4Ijp0cnVlLCJ0b2tlbklkIjoicXpxaXl2ZGRieHJzbWd0dHBzbGJnNHNodmEiLCJvcmdhbml6YXRpb24iOiJ0aGVkb3djaGVtaWNhbGNvbXBhbnlwcm9kdWN0aW9uZHpmdGFsODkiLCJ1c2VySWRzIjpbeyJ0eXBlIjoiVXNlciIsIm5hbWUiOiItMTI5MTQ1NDkyMiIsInByb3ZpZGVyIjoiRW1haWwgU2VjdXJpdHkgUHJvdmlkZXIifV0sInJvbGVzIjpbInF1ZXJ5RXhlY3V0b3IiXSwiaXNzIjoiU2VhcmNoQXBpIiwiZXhwIjoxNjk1MTIxMTgwLCJpYXQiOjE2OTUwMzQ3ODB9.IJV8wfamCyMOjpw-64Qt5DIZCr6c-H-ABxc08X9bz_Q',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'cookie': 'SESSION=aeaf9406-a377-49a2-a02b-3a7a1cc83d30',
    'origin': 'https://www.dow.com',
    'referer': 'https://www.dow.com/',
    'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }
    response_q1 = requests.request("POST", url_q1, headers=headers_q1, data=payload_q1, proxies=proxies)
    return response_q1.json()

###################################################################################################################################
# Query2: Get Dow List by ID
###################################################################################################################################
def query2(product_id2, url2):
    referer2 = "https://www.dow.com" + str(url2[8:])
    url2 = "https://www.dow.com/en-us/.trade.products.servlet." + str(product_id2) + ".json?filterByRealSub=true"
    payload2 = {}
    cookies2 = "OptanonAlertBoxClosed=2023-03-07T14:36:12.899Z; _abck=8AE1B6A0C82D7ABFCF7138A775B31D46~0~YAAQtxTfrYtkkw6HAQAAjtd0Rwn6Qc0UBVaiw1l7dBkuAUfpIfW8Xgl6H3VYCZO8XlMGxeKuvNew/BJqvwiqScKo/2mWXgSqAI0haM0pZhUN1Bya9Zyd+gwOmPk/Km8hKPILBm4rN6/GUECx9GE22Rsn8Ypt4JmXteTS6th+na79+1tOIS/4etHd7qs9VM48YIBM1v52YVkBcQ+YxuOruN5F00b8nfISXnnGjVG2+yQq3yUA3cvRPfMxCvO+lblgAJ/agAmA0BuMQbKhgvEqVBKEM/qjiSvAJ+tlhqKGi6lNAb3mh6pv2w/zAxQt6U9rVnLoA6oJwCCZEYNx2eK3D/7P19EcB6Fk4O1sXGrI30cA+v1xFGWessQYjpK89igLZZ/6RWA2ySv8hlNtgj4yc/3ItxVD~-1~-1~-1; mbox=session#75d48f65a5854db4a165c46e61ef033a#1680532954|PC#75d48f65a5854db4a165c46e61ef033a.37_0#1743775894; renderid=rend04; akaalb_dcdow-prod1=~op=DcDowComProd_LB:prod1-dcpub1|~rv=14~m=prod1-dcpub1:0|~os=974ebf39b3b5b4006d2c260db889f5f6~id=63a474bc6de4a8c9270e15feb75e9d7c; languageCode=en-us; country=FR; state=IDF; DCCLocale={%22country%22:%22FR%22%2C%22state%22:%22IDF%22}; AKA_A2=A; OptanonConsent=isGpcEnabled=0, datestamp=Fri+Sep+01+2023+10%3A31%3A41+GMT%2B0200+(Central+European+Summer+Time), version=202306.2.0, isIABGlobal=false, hosts=,consentId=c0cd6528-9330-4ff3-8aaa-7a8b3ce4923b, interactionCount=1, landingPath=NotLandingPage, 'groups=C0001%3A1%2CC0002%3A0%2CC0003%3A0%2CC0004%3A0', 'geolocation=DE%3BBW', AwaitingReconsent=false, browserGpcFlag=0"
    headers2 = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-DE,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
    'authority': 'www.dow.com',
    'cookie': cookies2,
    'referer': referer2,
    'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }
    response2 = []
    response = requests.request("GET", url2, headers=headers2, data=payload2)
    try:
        response2 = response.json()
    except requests.exceptions.RequestException as e:
        response2[0] = 'error_code'
        response2[1] = e

        pass
    finally:
        return response2

#####################################################################################################################################
# Query3: Get Dow List by ID and Page
#####################################################################################################################################
def query3(tradeProduct3, product_id3):
    url3 = "https://www.dow.com/en-us/.sds.doc.json?tradeProduct=" + str(tradeProduct3) + "&product=" + str(product_id3)
    referer3 = "https://www.dow.com" + str(url3[8:])
    cookies = "'OptanonAlertBoxClosed=2023-03-07T14:36:12.899Z; _abck=8AE1B6A0C82D7ABFCF7138A775B31D46~0~YAAQtxTfrYtkkw6HAQAAjtd0Rwn6Qc0UBVaiw1l7dBkuAUfpIfW8Xgl6H3VYCZO8XlMGxeKuvNew/BJqvwiqScKo/2mWXgSqAI0haM0pZhUN1Bya9Zyd+gwOmPk/Km8hKPILBm4rN6/GUECx9GE22Rsn8Ypt4JmXteTS6th+na79+1tOIS/4etHd7qs9VM48YIBM1v52YVkBcQ+YxuOruN5F00b8nfISXnnGjVG2+yQq3yUA3cvRPfMxCvO+lblgAJ/agAmA0BuMQbKhgvEqVBKEM/qjiSvAJ+tlhqKGi6lNAb3mh6pv2w/zAxQt6U9rVnLoA6oJwCCZEYNx2eK3D/7P19EcB6Fk4O1sXGrI30cA+v1xFGWessQYjpK89igLZZ/6RWA2ySv8hlNtgj4yc/3ItxVD~-1~-1~-1; mbox=session#75d48f65a5854db4a165c46e61ef033a#1680532954|PC#75d48f65a5854db4a165c46e61ef033a.37_0#1743775894; renderid=rend04; akaalb_dcdow-prod1=~op=DcDowComProd_LB:prod1-dcpub1|~rv=14~m=prod1-dcpub1:0|~os=974ebf39b3b5b4006d2c260db889f5f6~id=63a474bc6de4a8c9270e15feb75e9d7c; languageCode=en-us; country=FR; state=IDF; DCCLocale={%22country%22:%22FR%22%2C%22state%22:%22IDF%22}; AKA_A2=A; OptanonConsent=isGpcEnabled=0, 'datestamp=Fri+Sep+01+2023+10%3A21%3A18+GMT%2B0200+(Central+European+Summer+Time), 'version=202306.2.0, 'isIABGlobal=false, 'hosts=, 'consentId=c0cd6528-9330-4ff3-8aaa-7a8b3ce4923b, 'interactionCount=1, 'landingPath=NotLandingPage, 'groups=C0001%3A1%2CC0002%3A0%2CC0003%3A0%2CC0004%3A0, 'geolocation=DE%3BBW, 'AwaitingReconsent=false, 'browserGpcFlag=0'"
    headers3 = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-DE,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
    'authority': 'www.dow.com',
    'cookie': cookies,
    'referer': referer3,
    'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
    }

    res = requests.request("GET", url3, headers=headers3)
    return res.json()
######################################################################################################################################
# Query4: Download SDS File by tradeName, productCode, recordNumber
def getSDS(language,recordNumber, tradeProductCode, product_id,selectedCountryCode):
    url4 = "https://www.dow.com/content/dcc/en-us/doc-viewer-blank/.document.reader.svc"
    params4 = {
     'code': ''
    ,'languageJson' :''
    ,'language': language
    ,'documentType': 'SDS'
    ,'archiveKey': '//SDS'
    ,'recordNumber': recordNumber
    ,'materialNumber': ''
    ,'tradeProduct': tradeProductCode
    ,'product': product_id
    ,'title': ''
    ,'selectedCountry': selectedCountryCode
    ,'archiveId': ''
    ,'orderSalesOrg': ''
    ,'orderNumber': ''
    ,'deliver': ''
    }
    #headers4 = {'Cookie': 'akaalb_dcdow-prod1=~op=DcDowComProd_LB:prod1-dcpub2|~rv=34~m=prod1-dcpub2:0|~os=974ebf39b3b5b4006d2c260db889f5f6~id=b1a96ab38d26ba26715ee04bb3d93d85; renderid=rend02'}
    
    headers4 = {'Cookie': 'akaalb_dcdow-prod1=~op=DcDowComProd_LB:prod1-dcpub2|~rv=34~m=prod1-dcpub2:0|~os=974ebf39b3b5b4006d2c260db889f5f6~id=b1a96ab38d26ba26715ee04bb3d93d85; renderid=rend02'}
    
    response4 = requests.request("GET", url4, headers=headers4, params=params4)
    return response4.content, response4.status_code

#####################################################################################################################################
# Get DOW SDS List
#####################################################################################################################################
@cli.command('get_data')
def dowSDSList():
    DowSDSList = {}
    # Get Dow List|Query1
    numberOfResults=100
    excerptLength=200
    locale='en'
    q = ''
    firstResult=0
    totalCount = 20000
    while firstResult < totalCount:        
        response_Query1 = query1(numberOfResults, excerptLength, locale,q,firstResult)
        DowSDSList = response_Query1['results']
        totalCount = response_Query1['totalCount']
        #DowSDSList_hearer = response_Query1.headers
    
        with open(path + "_" + str(firstResult) + "_DowSDSList.json", 'w') as f:
            json.dump(DowSDSList, f)
            f.close()
        
        # Get Dow List|Query2, Query3, Query4 (Save SDS Files to Storage)
        for row in DowSDSList:
            # Start DB Transaction for DowSDSList
            title = row['title']
            #description = row['excerpt']
            #filename=row['uniqueId']
            if (row['raw'].get('ec_skus')) is not None and (row['raw']['ec_skus'][0] != 'customsilastic'):
                product_id = row['raw']['ec_skus'][0]
            else:
                continue
            url = row['uri']
            print("Q21: product_id: url", product_id, url,"################")
            # Get tradeProductCode|Query2
            response_Query2 = query2(product_id,url)
            if type(response_Query2) in (list, dict) and (len(response_Query2) > 0 and response_Query2[0].get('code')):
                for q2 in response_Query2:
                    tradeProductCode = q2['code']
                    # Get recordNumber, Languages, SDS File Url|Query3
                    print("Q3: tradeProductCode,product_id", tradeProductCode, product_id, "################")
                    response_Query3 = query3(tradeProductCode, product_id)
                    if type(response_Query3) is not str and response_Query3.get('sdsData') is not None:
                        selectedCountry_list = response_Query3['sdsData']
                        for q3 in selectedCountry_list:
                            if q3 is not None:
                                selectedCountry = q3
                                selectedCountryCode = selectedCountry_list[selectedCountry]['countryIsoCode']
                                for sdsData in selectedCountry_list[selectedCountry]['documents']:
                                    if sdsData  is not None:
                                        
                                        print("M4-2: language",sdsData['language'])
                                        print("M4-3: recordNumber", sdsData['recordNumber'])
                                        # Get SDS File|Query4
                                        print("M3-2: selectedCountryCode", selectedCountryCode)
                                        print("M3-2: product_id", product_id)
                                        print("M3-2: tradeProductCode", tradeProductCode)
                                        print("Write to DB: DowList")
                                        language = sdsData['language']                       
                                        recordNumber = sdsData['recordNumber']
                                        filename = "not_available"
                                        db.session.add(DowList(
                                             title=title
                                            , url=url
                                            , url_pdf=""
                                            , region=selectedCountryCode
                                            , description="not available"
                                            , filename=filename
                                            , language=language
                                            , product_id = product_id
                                            , trade_productCode=tradeProductCode
                                            , record_number=recordNumber
                                            , page= 1
                                        ))
                                        db.session.commit()
                    else:
                        print("Q3: error_code", response_Query3)
                        continue
            else:
                print("Q2: error_code", response_Query2)
                continue
        firstResult += numberOfResults
        print ("firstResult: ", firstResult)
        print ("###################################################")                                          
#####################################################################################################################################
# END: Get DOW SDS List
#####################################################################################################################################

#####################################################################################################################################
# START: DOW SDS Get SDS File and Save to Storage
#####################################################################################################################################
@cli.command('get_sds')
def get_sds():
    # TODO: add to config
    retry_count = 10
    retry_timeout = 5
    # Get Dow SDS List from DB
    dow_sds_files_list = db.session.query(DowList).filter(DowList.status == 'new' and DowList.language in ('EN', 'DE', 'FR', 'IT')) # type: ignore
    for sdsItem in dow_sds_files_list:
        try:
            if not None in (sdsItem.language,sdsItem.record_number, sdsItem.trade_productCode, sdsItem.product_id, sdsItem.region):
                response_Query4 = getSDS(sdsItem.language,sdsItem.record_number, sdsItem.trade_productCode, sdsItem.product_id, sdsItem.region)
            if response_Query4 is not None and response_Query4[1] == "200":
                # clear retry_count, retry_timeout counters TODO: add to config
                retry_count = 10
                retry_timeout = 5
                # Save SDS File to Storage
                # Create new folder if not exists
                sdsPath = path + str(sdsItem.language) + "/"
                if not os.path.exists(sdsPath):
                    os.makedirs(sdsPath)
                # Generate filename
                filename = path + str(sdsItem.language) + "/" + str(sdsItem.product_id) + "_" + str(sdsItem.trade_productCode) + "_" + str(sdsItem.record_number) + "_lang_" + str(sdsItem.region) + "_" + str(sdsItem.language) + str('.pdf')
                
                # Write SDS File to Storage
                with open(filename, 'wb') as f:
                    f.write(response_Query4[0])
                    f.close()
                    # Update status in DB
                    sdsItem.status = 'done'
                    db.session.commit()
            elif response_Query4[1] == 403:
                # clear retry_count, retry_timeout counters TODO: add to config
                retry_count = 10
                retry_timeout = 5
                # Update status in DB
                sdsItem.status = response_Query4[1]
                db.session.commit()
                exit()
            elif response_Query4[1] == 502 or 503 or 504 and retry_count > 0: # TODO: add to config
                # clear retry_count, retry_timeout counters TODO: add to config
                retry_count -= 1
                retry_timeout += 5
                # Update status in DB
                sdsItem.status = response_Query4[1]
                db.session.commit()
                time.sleep(retry_timeout)
                continue
            elif retry_count == 0:
                # Update status in DB
                sdsItem.status = response_Query4[1]
                db.session.commit()
                # TODO: Notify Admin
                exit()
            else:
                # Update status in DB
                sdsItem.status = response_Query4[1]
                db.session.commit()
                continue
        except requests.exceptions.RequestException as e:
            print("Request Query4: Get SDS error_code", e)
            sdsItem.status = 'error'
            pass
            
        finally:
            print("dow_sds_files_list", sdsItem.title)
            print("url",sdsItem.url)
            print("url_pdf",sdsItem.url_pdf)
            print("filename",sdsItem.filename)
            print("language",sdsItem.language)
            print("region",sdsItem.region)
            print("product_id",sdsItem.product_id)
            print("trade_productCode",sdsItem.trade_productCode)
            print("record_number",sdsItem.record_number)
            print("page",sdsItem.page)
            print("HTTP Status Code",response_Query4[1])
            print("status",sdsItem.status,"\n")
            #time.sleep(1)     
    
    print("END Processing: Dow SDS Download")
#####################################################################################################################################
# END: DOW SDS Get SDS File and Save to Storage
#####################################################################################################################################
if __name__ == "__main__":
    cli()

