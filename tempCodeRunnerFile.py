import os

from SendMail import MailPhotoSender
from dotenv import load_dotenv

if __name__ == "__main__":
    # Load environment variables from infos.env file
    load_dotenv(dotenv_path="infos.env")

    # Email configuration from environment variables
    sender_email = os.getenv("FROM_EMAIL")
    recipient_email = os.getenv("TO_EMAIL")
    password = os.getenv("PASSWORD")

    subject = "Graph Output"
    body = "Please find the attached graph generated from visits_today.csv."
    attachment_path = "graph_output.png"

    # Initialize the MailPhotoSender class
    mail_sender = MailPhotoSender(sender_email, password, "smtp.gmail.com", 587)
    
    # Send the email with the graph attachment
    mail_sender.send_mail_with_image(
        subject=subject,
        body=body,
        to_email=recipient_email,
        image_path=attachment_path
    )
