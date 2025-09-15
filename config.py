import os
from dotenv import load_dotenv
load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")
TWILIO_WA_PHONE = os.getenv("TWILIO_WA_PHONE")  # WhatsApp Twilio number
TWILIO_DEST_PHONE = os.getenv("TWILIO_DEST_PHONE")
TWILIO_DEST_WA = os.getenv("TWILIO_DEST_WA")