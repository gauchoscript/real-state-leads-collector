import pytest
import pytz
import json
from datetime import datetime, timedelta
from src.services.listings import Listings
from src.services.persistor import Persistor

class MockLoginResponse:
  @staticmethod
  def json():
    return {'id_token': 'mocked_token'}

class MockGetListingResponse:
  def __init__(self, response):
    self.status_code = response['status_code']
    self.headers = {'Content-Type': 'application/json'}
    self._json_data = {
      'data': response['data'],
      'searchFilter': {'totalPages': 3}
    }
    self.content = json.dumps(self._json_data).encode('utf-8')
    self.text = json.dumps(self._json_data)
  
  def json(self):
    return self._json_data

class MockGetListingDetailsResponse:
  _tz = pytz.timezone("America/Argentina/Buenos_Aires")
  _now = datetime.now(_tz)
  data = [
    {
      'id': 1, 
      'mlsid': '1234567-890', 
      'address': {'neighborhood': 'Neighborhood A'}, 
      'question': {
        'question': [
          { #old question outside 3 days window
            'portal': 'Real State Portal 1',
            'from': {
              'first_name': 'Johny',
              'last_name': 'Doe',
              'email': 'jhony@doe.com', 
              'phone': {'number': '123456789'}
            },
            'text': 'I am interested in this property.',
            'received': (_now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
          },
          {
            'portal': 'Real State Portal 1',
            'from': {
              'first_name': 'John',
              'last_name': 'Doe',
              'email': 'jhon@doe.com', 
              'phone': {'number': '123456789'}
            },
            'text': 'I am interested in this property.',
            'received': _now.strftime("%Y-%m-%d %H:%M:%S")
          },
          {
            'portal': 'Real State Portal 2',
            'from': {
              'first_name': 'Jane',
              'last_name': 'Smith',
              'email': 'jane@smith.com', 
              'phone': {'number': '987654321'}
            },
            'text': 'Please provide more details.',
            'received': _now.strftime("%Y-%m-%d %H:%M:%S") 
          }
        ]
      }
    },
    {
      'id': 4, 
      'mlsid': '7654321-098', 
      'address': {'city': 'City B'}, 
      'question': {
        'question': [
          {
            'portal': 'Real State Portal 1',
            'from': {
              'first_name': 'Alice',
              'last_name': 'Johnson',
              'email': 'alice@jhonson',
              'phone': {'number': '555666777'}
            },
            'text': 'Is this property still available?',
            'received': _now.strftime("%Y-%m-%d %H:%M:%S")
          },
          { #duplicated question within some minutes of difference to test lead deduplication functionallity
            'portal': 'Real State Portal 1',
            'from': {
              'first_name': 'Alice',
              'last_name': 'Johnson',
              'email': 'alice@jhonson',
              'phone': {'number': '555666777'}
            },
            'text': 'Is this property still available?',
            'received': _now.strftime("%Y-%m-%d %H:%M:%S")
          }
        ]
      }
    }
  ]
  
  def __init__(self, listing_id):
    self.return_value = next((item for item in self.data if item['id'] == listing_id), None)
    
  def json(self):
    return self.return_value

@pytest.fixture
def mock_login():
  return lambda *args, **kwargs: MockLoginResponse()

@pytest.fixture
def mock_envs_and_requests(monkeypatch, mock_login):
  #Arrange
  mock_listing_url = "https://realstate.com/api/listings"
  mock_listing_details_url = "https://realstate.com/api/listing-details"
  monkeypatch.setenv("LISTINGS_URL", mock_listing_url)
  monkeypatch.setenv("LISTING_DETAILS_URL", mock_listing_details_url)
  
  # share the same instance to keep state between calls
  responses = [
    {'status_code': 200, 'data': [{'id': 1, 'countContacts': 5, 'status': 'active'}, {'id': 2, 'countContacts': 0, 'status': 'active'}]},
    {'status_code': 500, 'data': []},
    {'status_code': 200, 'data': [{'id': 3, 'countContacts': 3, 'status': 'inactive'}, {'id': 4, 'countContacts': 2, 'status': 'active'}]}
  ]

  def mock_get(url, *args, **kwargs):
    if url == mock_listing_url:
      return MockGetListingResponse(responses.pop(0) if responses else {'status_code': 200, 'data': []})
    
    listing_id = int(url.split('/')[-1])
    return MockGetListingDetailsResponse(listing_id)

  monkeypatch.setattr("src.services.listings.requests.post", mock_login)
  monkeypatch.setattr("src.services.listings.requests.get", mock_get)
  monkeypatch.setattr("src.services.listings.time.sleep", lambda x: None)

def test_get_contacted_active_sale_listings(mock_envs_and_requests):
  sut = Listings()
  
  recent_contacted_listings = sut.get_listings()

  assert len(recent_contacted_listings) == 2
  assert recent_contacted_listings[0]['id'] == 1
  assert recent_contacted_listings[1]['id'] == 4

def test_get_dedupicated_leads_from_recent_contacted_listings(mock_envs_and_requests):
  sut = Listings()

  leads = sut.get_leads()

  assert len(leads) == 3
  assert leads[0].email == 'jhon@doe.com'
  assert leads[1].email == 'jane@smith.com'
  assert leads[2].email == 'alice@jhonson'

def test_leads_saved_correctly_in_xlsx_file(mock_envs_and_requests, tmp_path):
  real_state_service = Listings()
  leads = real_state_service.get_leads()
  sut = Persistor(tmp_path)

  file_path = sut.save_to_xlsx(leads)

  assert file_path.exists()
  assert file_path.stat().st_size > 0
