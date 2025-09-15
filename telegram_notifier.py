import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{8305256746:AAGeJmNUDLyO-8MTEEMpVoFFO863U9I2zW8}/sendMessage"
    payload = {"5646679766": 5646679766, "text": message}
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.ok
    except Exception as e:
        print("Error enviando Telegram:", e)
        return False