import glob
import os
import time
from dataclasses import asdict
from pathlib import Path

import pandas

SERVICES_DIR = Path(__file__).resolve().parent
SRC_DIR = SERVICES_DIR.parent
BASE_DIR = SRC_DIR.parent


class Persistor:
    def __init__(self, folder_path=BASE_DIR / "output"):
        self._folder_path = folder_path
        self._folder_path.mkdir(exist_ok=True)

    def _get_filename(self):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        return self._folder_path / f"relevant_listings_{timestamp}.xlsx"

    def save(self, leads):
        filename = self._get_filename()

        data = [asdict(lead) for lead in leads]

        dataframe = pandas.DataFrame(data)
        dataframe.columns = [
            "MLS ID",
            "Portal",
            "Recibido",
            "Zona",
            "Nombre",
            "Apellido",
            "Email",
            "Telefono",
            "Mensaje",
        ]

        dataframe.to_excel(filename, index=False)
        return filename

    def get_latest_leads_file(self):
        pattern = os.path.join(self._folder_path, "relevant_listings_*.xlsx")
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
