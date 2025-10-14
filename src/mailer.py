from dotenv import load_dotenv

load_dotenv()

from src.services.email_sender import EmailSender


def main():
    email_sender = EmailSender()
    email_sender.send_email()


if __name__ == "__main__":
    main()
