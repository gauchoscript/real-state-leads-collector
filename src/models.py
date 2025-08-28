import datetime
from dataclasses import dataclass

@dataclass
class Lead:
    id: int
    portal: str
    received: datetime
    zone: str
    first_name: str
    last_name: str
    email: str
    phone: str
    message: str