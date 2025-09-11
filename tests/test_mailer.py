from src.services.lead_files import LeadsFilesFinder
from src.mailer import EmailSender

class FakeSMTP:
  def __init__(self):
    self.sent_messages = []

  def starttls(self):
    pass

  def login(self, sender_email, sender_password):
    pass

  def sendmail(self, from_addr, to_addr, msg):
    self.sent_messages.append((from_addr, to_addr, msg))

  def quit(self):
    pass

def test_email_sents_successfully_when_leads_file_exists(monkeypatch, tmp_path):
  #Arrange
  fake_smtp = FakeSMTP()
  monkeypatch.setattr("smtplib.SMTP", lambda smtp_server, smtp_port: fake_smtp)

  tmp_filename = "relevant_listings_test.xlsx"
  tmp_file = tmp_path / tmp_filename
  tmp_file.touch()
  
  tmp_list_finder = LeadsFilesFinder(tmp_path)
  monkeypatch.setattr("src.services.lead_files.LeadsFilesFinder.get_latest_leads_file", tmp_list_finder.get_latest_leads_file)

  test_sender_email = 'sender_email@test.com'
  test_recipient_email = 'recipient_email@test.com'
  
  sut = EmailSender('smtp.test.com', 587, test_sender_email)
  
  #Act  
  sent = sut.send_email(test_recipient_email)

  #Assert
  assert sent == True
  assert len(fake_smtp.sent_messages) == 1
  assert fake_smtp.sent_messages[0][0] == test_sender_email
  assert fake_smtp.sent_messages[0][1] == test_recipient_email
  assert fake_smtp.sent_messages[0][2].find(tmp_filename) != -1