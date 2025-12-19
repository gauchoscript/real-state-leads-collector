import os
import sys

from dotenv import load_dotenv

load_dotenv()

from src.models import EmailConfig
from src.services.email_sender import EmailSender
from src.services.persistor import Persistor


def main():
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    if not sender_email or not sender_password:
        sys.exit("SENDER_EMAIL and SENDER_PASSWORD environment variables must be set.")

    email_config = EmailConfig(sender_email, sender_password)

    email_sender = EmailSender(email_config, Persistor())
    email_sender.send()


if __name__ == "__main__":
    main()
