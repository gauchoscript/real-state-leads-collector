import time
import sys
from api import ClientAPI
from persistence import Persistence

client = ClientAPI()

total_start = time.time()
sys.stdout.write("Starting to fetch listings...\n")
sys.stdout.flush()

recent_contacted_listings = client.get_listings()
leads = []

if (len(recent_contacted_listings) > 0):
  leads = client.get_leads(recent_contacted_listings)

total_end = time.time()
sys.stdout.write(f"Total leads found: {len(leads)}\n")
sys.stdout.write(f"Total time taken: {total_end - total_start:.2f} seconds\n")
sys.stdout.flush()

persistence = Persistence()
persistence.save_to_xlsx(leads)