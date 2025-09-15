import requests
import os

# Tus credenciales (también pueden venir de variables de entorno)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8305256746:AAGeJmNUDLyO-8MTEEMpVoFFO863U9I2zW8")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5646679766")

def send_telegram(message: str, chat_id: str = None) -> bool:
    """
    Envía mensaje a Telegram.
    Si no se pasa chat_id, usa el global.
    """
    cid = chat_id or TELEGRAM_CHAT_ID
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": cid, "text": message, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.ok
    except Exception as e:
        print("Error enviando Telegram:", e)
        return False