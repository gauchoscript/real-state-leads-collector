import time
import pandas
from dataclasses import asdict
from src.constants import BASE_DIR

class Persistence:
  def __init__(self, folder_path=BASE_DIR / 'output'):
    self.folder_path = folder_path
    self.folder_path.mkdir(exist_ok=True)

  def _get_filename(self):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    return self.folder_path / f"relevant_listings_{timestamp}.xlsx"

  def save_to_xlsx(self, leads):
    filename = self._get_filename()

    data = [asdict(lead) for lead in leads]

    dataframe = pandas.DataFrame(data)
    dataframe.columns = ['MLS ID', 'Portal', 'Recibido', 'Zona', 'Nombre', 'Apellido', 'Email', 'Telefono', 'Mensaje']

    dataframe.to_excel(filename, index=False)
    return filename
