import requests
import time
import sys
import random
import pytz
import os
from datetime import datetime, timedelta
from models import Lead

class RealStateService:
  token = ''
  offices = os.getenv('OFFICE_IDS').split(',')
  recent_contacted_listings = []

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
        if item['countContacts'] > 0 and item['status'] == 'active':
          listing_id = item['id']
          sys.stdout.write(f"Fetching details for listing {listing_id}...\n")
          sys.stdout.flush()
          start = time.time()
          time.sleep(random.uniform(0.1, 1))
          # make this api calls persist every 20 pages or so that way they're not completly lost if some error happens
          self.recent_contacted_listings.append(self.get_listing_details(listing_id))
          end = time.time()
          sys.stdout.write(f" Done in {end - start:.2f} seconds.\n")
          sys.stdout.flush()

    total_pages = response['searchFilter']['totalPages']
    sys.stdout.write(f"Total pages: {total_pages}, \n")
    sys.stdout.flush()
    if page < min(total_pages, 300):
        time.sleep(random.uniform(0.1, 1))
        return self.get_listings(page + 1, page_size)
    else:
      return self.recent_contacted_listings

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
      zone = ''
      for key in ['neighborhood', 'city', 'subregion', 'region']:
        zone = listing['address'].get(key)
        if zone:
          break
      
      last_question_hash = None
      for question in listing['question']['question']:
        question_date = tz.localize(datetime.strptime(question['received'], "%Y-%m-%d %H:%M:%S"))
        question_hash = f"{question['from'].get('email', '')}_{question['from'].get('phone', {}).get('number')}"
        
        if three_days_ago <= question_date and question_hash != last_question_hash:
          listing_rows.append(Lead(
            listing['mlsid'], 
            question['portal'], 
            question['received'],
            zone, 
            question['from']['first_name'],
            question['from']['last_name'],
            question['from']['email'],
            question['from']['phone']['number'],
            question['text'].replace('\n', ' ')
          ))
          last_question_hash = question_hash
    return listing_rows