import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client
from config import *

def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_USER
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, EMAIL_USER, msg.as_string())

def send_sms(body):
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    client.messages.create(body=body, from_=TWILIO_PHONE, to=TWILIO_DEST_PHONE)

def send_whatsapp(body):
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    client.messages.create(body=body, from_=f"whatsapp:{TWILIO_WA_PHONE}", to=f"whatsapp:{TWILIO_DEST_WA}")

def send_alert(message):
    print("Enviando alertas...")
    send_email("Alerta de Monitoreo", message)
    send_sms(message)
    send_whatsapp(message)