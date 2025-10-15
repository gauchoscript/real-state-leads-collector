import os
import smtplib
import sys
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.services.persistor import Persistor


class EmailSender:
    def __init__(
        self,
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        sender_email=os.getenv("SENDER_EMAIL"),
        sender_password=os.getenv("SENDER_PASSWORD"),
        persistor=None,
    ):
        self._smtp_server = smtp_server
        self._smtp_port = smtp_port
        self._sender_email = sender_email
        self._sender_password = sender_password
        self._persistor = persistor or Persistor()

    def _attach_leads_file(self, message):
        latest_leads_file = self._persistor.get_latest_leads_file()
        if not latest_leads_file:
            sys.exit("No leads file found to attach.")

        with open(latest_leads_file, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f'attachment; filename="{os.path.basename(latest_leads_file)}"',
        )
        message.attach(part)

        return message

    def _create_message(self, recipient_email):
        message = MIMEMultipart()
        message["From"] = self._sender_email
        message["To"] = recipient_email
        message["Subject"] = "Leads Report"

        body = "Please find the attached leads report."
        message.attach(MIMEText(body, "plain"))

        message = self._attach_leads_file(message)

        return message.as_string()

    def send(self, recipient_email=os.getenv("RECIPIENT_EMAIL")):
        message = self._create_message(recipient_email)

        try:
            server = smtplib.SMTP(self._smtp_server, self._smtp_port)
            server.starttls()
            server.login(self._sender_email, self._sender_password)
            server.sendmail(self._sender_email, recipient_email, message)
            server.quit()
            sys.stdout.write("Email sent successfully!")
            return True
        except Exception as e:
            sys.stdout.write(f"Error: {e}")
            return False
