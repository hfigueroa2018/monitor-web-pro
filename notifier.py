import os
from telegram_notifier import send_telegram

DEFAULT_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_alert(message: str, chat_id: str = None):
    cid = int(chat_id or DEFAULT_CHAT_ID)
    if not cid:
        print("Sin chat_id configurado")
        return False
    return send_telegram(message, cid)