import requests
import os

# Lee desde variables de entorno (ya están en .env o en Render)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8305256746:AAGeJmNUDLyO-8MTEEMpVoFFO863U9I2zW8")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5646679766")

def send_telegram(message: str) -> bool:
    """Envía un mensaje por Telegram y devuelve True si tuvo éxito."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.ok
    except Exception as e:
        print("Error enviando Telegram:", e)
        return False