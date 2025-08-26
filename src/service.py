import requests
import time
import sys
import random
import pytz
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from models import Lead

load_dotenv()

class RealStateService:
  token = ''
  offices = os.getenv('OFFICE_IDS').split(',')

  def __init__(self, username=os.getenv('USERNAME'), password=os.getenv('PASSWORD')):
    self.token = self.login(username, password)

  def login(self, username, password):
    payload = {
        "user": {
          "username": username,
          "password": password
        }
    }
    response = requests.post(os.getenv('LOGIN_URL') , json=payload)      
    return response.json()['id_token']
  
  def get_listings(self, page=1, page_size=10, offices=[]):
    recent_contacted_listings = []
    sys.stdout.write(f"Fetching page {page}...\n")
    sys.stdout.flush()
    params = {
        "type": "sale",
        "associateStatus": "active",
        "combineStatus": "Activas",
        "orderby": "-updated_on",
        "page": page,
        "page_size": page_size,
        "byoffice[]": offices,
    }
    headers = {
        "Authorization": f"Bearer {self.token}"
    }
    start = time.time()
    response = requests.get(os.getenv('LISTINGS_URL'), params=params, headers=headers)
    end = time.time()
    sys.stdout.write(f" Done in {end - start:.2f} seconds.\n")
    response = response.json()

    if 'data' in response:
      for item in response['data']:
        if item['countContacts'] > 0:
          listing_id = item['id']
          time.sleep(random.uniform(0.1, 1))
          sys.stdout.write(f"Fetching details for listing {listing_id}...\n")
          sys.stdout.flush()
          start = time.time()
          recent_contacted_listings.append(self.get_listing_details(listing_id))
          end = time.time()
          sys.stdout.write(f" Done in {end - start:.2f} seconds.\n")
          sys.stdout.flush()
  
    total_pages = response['searchFilter']['totalPages'];
    sys.stdout.write(f"Total pages: {total_pages}, \n")
    sys.stdout.flush()
    if page < min(total_pages, 300):
        time.sleep(random.uniform(0.1, 1))
        self.get_listings(page + 1, page_size)
    else:
      return recent_contacted_listings

  def get_listing_details(self, listing_id):
    url = f"{os.getenv('LISTING_DETAILS_URL')}/{listing_id}"
    headers = {
        "Authorization": f"Bearer {self.token}"
    }
    
    response = requests.get(url, headers=headers)
    return response.json()

  def get_leads(self, recent_contacted_listings):
    listing_rows = []
    tz = pytz.timezone("America/Argentina/Buenos_Aires")
    now = datetime.now(tz)
    three_days_ago = now - timedelta(days=3)

    for listing in recent_contacted_listings:
      for question in listing['question']['question']:
        question_date = tz.localize(datetime.strptime(question['received'], "%Y-%m-%d %H:%M:%S"))
        
        if three_days_ago <= question_date:
          listing_rows.append(Lead(
            listing['mlsid'], 
            question['portal'], 
            question['received'], 
            question['from']['first_name'],
            question['from']['last_name'],
            question['from']['email'],
            question['from']['phone']['number'],
            question['text'].replace('\n', ' ')
          ))
    return listing_rows