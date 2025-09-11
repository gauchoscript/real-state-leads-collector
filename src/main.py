from dotenv import load_dotenv
load_dotenv()

import time
import sys
from src.service import RealStateService
from src.persistor import Persistor

def main():
  real_state_service = RealStateService()

  total_start = time.time()
  sys.stdout.write("Starting to fetch listings...\n")
  sys.stdout.flush()

  leads = real_state_service.get_leads()

  total_end = time.time()
  sys.stdout.write(f"Total leads found: {len(leads)}\n")
  sys.stdout.write(f"Total time taken: {total_end - total_start:.2f} seconds\n")
  sys.stdout.flush()

  if (len(leads) > 0):
    persistence = Persistor()
    persistence.save_to_xlsx(leads)

if __name__ == "__main__":
  main()