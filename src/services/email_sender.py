import os
import smtplib
import sys
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.models import EmailConfig
from src.services.persistor import Persistor


class EmailSender:
    def __init__(
        self,
        config: EmailConfig,
        persistor: Persistor,
    ):
        self._config = config
        self._persistor = persistor

    def _attach_leads_file(self, message: MIMEMultipart):
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

    def _create_message(self, recipient_email: str):
        message = MIMEMultipart()
        message["From"] = self._config.sender_email
        message["To"] = recipient_email
        message["Subject"] = "Leads Report"

        body = "Please find the attached leads report."
        message.attach(MIMEText(body, "plain"))

        message = self._attach_leads_file(message)

        return message.as_string()

    def send(self, recipient_email: str | None = os.getenv("RECIPIENT_EMAIL")):
        if not recipient_email:
            raise ValueError(
                "Recipient email must be provided either as an argument or environment variable."
            )

        message = self._create_message(recipient_email)

        try:
            server = smtplib.SMTP(self._config.smtp_server, self._config.smtp_port)
            server.starttls()
            server.login(self._config.sender_email, self._config.sender_password)
            server.sendmail(self._config.sender_email, recipient_email, message)
            server.quit()
            sys.stdout.write("Email sent successfully!")
            return True
        except Exception as e:
            sys.stdout.write(f"Error: {e}")
            return False
