import os
from telegram_notifier import send_telegram

DEFAULT_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_alert(message: str, chat_id: str = None):
    try:
        # Permitir que telegram_notifier aplique su default si chat_id es None
        return send_telegram(message, chat_id or DEFAULT_CHAT_ID)
    except Exception as e:
        print("[NOTIFIER] Error enviando alerta:", e)
        return False