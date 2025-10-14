from dotenv import load_dotenv

load_dotenv()

import time
import sys
from src.services.listings import Listings
from src.services.persistor import Persistor


def main():
    real_state_service = Listings()

    total_start = time.time()
    sys.stdout.write("Starting to fetch listings...\n")
    sys.stdout.flush()

    leads = real_state_service.get_leads()

    total_end = time.time()
    sys.stdout.write(f"Total leads found: {len(leads)}\n")
    sys.stdout.write(f"Total time taken: {total_end - total_start:.2f} seconds\n")
    sys.stdout.flush()

    if len(leads) > 0:
        persistor = Persistor()
        persistor.save(leads)


if __name__ == "__main__":
    main()
