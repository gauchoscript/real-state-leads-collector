import os
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


@dataclass
class EmailConfig:
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    sender_email: str = os.getenv("SENDER_EMAIL")
    sender_password: str = os.getenv("SENDER_PASSWORD")
