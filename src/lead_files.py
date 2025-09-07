import glob
import os
from datetime import datetime
from src.constants import BASE_DIR

class LeadsFilesFinder:
  def __init__(self, folder_path=BASE_DIR / "output"):
    self.folder_path = folder_path

  def get_latest_leads_file(self):
    pattern = os.path.join(self.folder_path, "relevant_listings_*.xlsx")
    files = glob.glob(pattern)

    if not files:
        return None
    
    latest_file = max(files, key=os.path.getmtime)

    # Optional: Check if file is from last 24 hours
    """ file_time = os.path.getmtime(latest_file)
    file_datetime = datetime.fromtimestamp(file_time)
    hours_old = (datetime.now() - file_datetime).total_seconds() / 3600
    
    if hours_old > 48:  # File is older than 48 hours
        print(f"Warning: Latest file is {hours_old:.1f} hours old") """
    
    return latest_file