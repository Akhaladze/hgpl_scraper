# Selenium 
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Flask
import sys
sys.path.append('/home/gnet/hgpl_scraper/project/connectors/')
from flask import Flask, request, jsonify, config
from flask.cli import FlaskGroup, click, cli
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB, ARRAY, UUID, TIMESTAMP
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey


# Models
import models as models
from models import db, Connectors, ConnectorData, Metadata, BasfListEN, BasfListOther, DowList

# Selenium options
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--headless")
driver = webdriver.Chrome(options=options, keep_alive=True)
driver.implicitly_wait(5)





@cli.command("get_dowlist")
def get_dowlist():
    '''
    Get DOW SDS files from list
    '''

    # DOW Pcraping Scenarios:
    #############################################################################################################
    #  Get list of SDS files
    # Save list of SDS files to DB
    # Check if SDS exists for each elements from list:
    # If (SDS exists) => get URL and and save to DB
    # Else (SDS does not exist) => skip and save to DB
    #############################################################################################################

    # Page counter options
    page_counter = 0
    item_counter = 0
    page_items = 100
    page_offset = 0
        
    # DOW website pagination loop
    while page_counter < 100:

        url='https://www.dow.com/en-us/support/sds-finder.html#q=1&numberOfResults=' + str(page_items) + '&first=' + str(page_offset)    
        
        driver.get(url)
        driver.find_element(By.ID, 'onetrust-accept-btn-handler').click()
        elements = driver.find_elements(By.CLASS_NAME, 'CoveoResultLink')
        
        # SDS (DOW Pdocucts) List processing
        for e in elements:
            if e.get_attribute('href') is not None and e.get_attribute('href').endswith('#tech-content') and e.get_attribute('href').startswith('https://www.dow.com/en-us/'):
                db.session.add(DowList(url=e.get_attribute('href'), filename=e.get_attribute('href').split('/')[-1], lang=e.get_attribute('href').split('/')[-2], region=e.get_attribute('href').split('/')[-3], page=page_counter))
                db.session.commit()
            print(e.get_attribute('href'))
            print(e.text)
        item_counter += 1

    page_counter += 1
    page_offset += page_items
    item_counter = 0
    driver.quit()
    print ("Page count: ", page_counter, "Page offset: ", page_offset)

# DOW SDS files download and save to Storage
@cli.command("get_dowpdf")
def get_dowpdf():
    '''
    Scrapping DOW SDS from product page and save to Storage
    '''
    page_items = 100
    # Prepare list of SDS files for download
    list = DowList.query.all()

    while page_counter < len(list):

        url= str(list[page_counter].url)    
        
        driver.get(url)
        # Select nested DOM elements by ID = "safety-data-sheet"
        
        # Click on "Accept" button

        driver.find_element(By.ID, 'onetrust-accept-btn-handler').click()
        elements = driver.find_elements(By.CLASS_NAME, 'CoveoResultLink')
        
        # Page items extraction
        for e in elements:
            if e.get_attribute('href') is not None and e.get_attribute('href').endswith('#tech-content') and e.get_attribute('href').startswith('https://www.dow.com/en-us/'):
                db.session.add(DowList(url=e.get_attribute('href'), filename=e.get_attribute('href').split('/')[-1], lang=e.get_attribute('href').split('/')[-2], region=e.get_attribute('href').split('/')[-3], page=page_counter))
                db.session.commit()
            print(e.get_attribute('href'))
            print(e.text)

            item_counter += 1

        page_counter += 1
        page_offset += page_items
        item_counter = 0
    driver.quit()
    print ("Page count: ", page_counter, "Page offset: ", page_offset)