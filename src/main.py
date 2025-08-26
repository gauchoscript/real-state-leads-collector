import time
import sys
from service import RealStateService
from persistence import Persistence

def main():
  real_state_service = RealStateService()

  total_start = time.time()
  sys.stdout.write("Starting to fetch listings...\n")
  sys.stdout.flush()

  recent_contacted_listings = real_state_service.get_listings()
  leads = []

  if (len(recent_contacted_listings) > 0):
    leads = real_state_service.get_leads(recent_contacted_listings)

  total_end = time.time()
  sys.stdout.write(f"Total leads found: {len(leads)}\n")
  sys.stdout.write(f"Total time taken: {total_end - total_start:.2f} seconds\n")
  sys.stdout.flush()

  if (len(leads) > 0):
    persistence = Persistence()
    persistence.save_to_xlsx(leads)

if __name__ == "__main__":
  main()