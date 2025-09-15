import os
from dotenv import load_dotenv
load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

TELEGRAM_TOKEN=8305256746:AAGeJmNUDLyO-8MTEEMpVoFFO863U9I2zW8
TELEGRAM_CHAT_ID=5646679766

