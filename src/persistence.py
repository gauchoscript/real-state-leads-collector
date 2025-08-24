import time
import pandas
from dataclasses import asdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PARENT_DIR = BASE_DIR.parent

class Persistence:
  def save_to_xlsx(self, leads):
    folder_path = PARENT_DIR / 'output'
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = folder_path / f"relevant_listings_{timestamp}.xlsx"

    data = [asdict(lead) for lead in leads]

    dataframe = pandas.DataFrame(data)
    dataframe.columns = ['MLS ID', 'Portal', 'Recibido', 'Nombre', 'Apellido', 'Email', 'Telefono', 'Mensaje']

    dataframe.to_excel(filename, index=False)
