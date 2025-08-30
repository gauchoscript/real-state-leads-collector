import smtplib
import os
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from lead_files import LeadsFilesFinder
from dotenv import load_dotenv

class EmailSender:
  # Email settings
  smtp_server = 'smtp.gmail.com'
  smtp_port = 587
  sender_email = ''
  sender_password = ''

  def __init__(self, smtp_server, smtp_port, sender_email, sender_password):
    self.smtp_server = smtp_server
    self.smtp_port = smtp_port
    self.sender_email = sender_email
    self.sender_password = sender_password
    
  def send_email(self, recipient_email=''):
    # Create email
    msg = MIMEMultipart()
    msg['From'] = self.sender_email
    msg['To'] = recipient_email
    msg['Subject'] = 'Leads Report'
    
    # Email body
    body = 'Please find the leads report attached.'
    msg.attach(MIMEText(body, 'plain'))
    
    latest_leads_file = LeadsFilesFinder.get_latest_leads_file() 

    if not latest_leads_file:
        sys.stdout.write("No leads file found to attach.")
        return False
    
    filename = os.path.basename(latest_leads_file)

    # Attach file
    with open(latest_leads_file, "rb") as attachment:
      part = MIMEBase('application', 'octet-stream')
      part.set_payload(attachment.read())

    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
    msg.attach(part)
    
    # Send email
    try:
        server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        server.starttls()
        server.login(self.sender_email, self.sender_password)
        server.sendmail(self.sender_email, recipient_email, msg.as_string())
        server.quit()
        sys.stdout.write("Email sent successfully!")
    except Exception as e:
        sys.stdout.write(f"Error: {e}")

def main():
  load_dotenv()
  
  email_sender = EmailSender(
      smtp_server="smtp.gmail.com",
      smtp_port=587,
      sender_email=os.getenv('SENDER_EMAIL'),
      sender_password=os.getenv('SENDER_PASSWORD')
  )
  email_sender.send_email(recipient_email=os.getenv('RECIPIENT_EMAIL'))

if __name__ == "__main__":
    main()