from dataclasses import dataclass
from datetime import datetime


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


@dataclass
class EmailConfig:
    sender_email: str
    sender_password: str
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
